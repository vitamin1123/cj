from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from functools import lru_cache
import orjson
import jwt
import bcrypt
from datetime import datetime, timedelta
import os
import aiofiles
from pathlib import Path
import uuid
from contextlib import asynccontextmanager
import httpx
import asyncio

# 配置
DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/database_name"
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
UPLOAD_DIR = "uploads"

# 微信配置
WECHAT_APP_ID = "wxc3d4a60a6dc54cdf"
WECHAT_APP_SECRET = "2b154ea94a9d9cb0ab7f3fe104336f1b"

# 创建上传目录
Path(UPLOAD_DIR).mkdir(exist_ok=True)

# 全局变量存储微信access_token
wechat_access_token_cache = {
    "token": None,
    "expires_at": None
}

# 数据库模型
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WechatUser(SQLModel, table=True):
    __tablename__ = "wechat_users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    openid: str = Field(unique=True, index=True)
    unionid: Optional[str] = Field(default=None, index=True)
    subscribe: int = Field(default=0)  # 是否关注公众号
    language: Optional[str] = Field(default="zh_CN")
    subscribe_time: Optional[int] = Field(default=None)  # 关注时间戳
    remark: Optional[str] = Field(default=None)
    groupid: Optional[int] = Field(default=None)
    subscribe_scene: Optional[str] = Field(default=None)
    qr_scene: Optional[int] = Field(default=None)
    qr_scene_str: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(SQLModel):
    username: str
    email: str
    password: str

class UserResponse(SQLModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

class WechatUserResponse(SQLModel):
    openid: str
    unionid: Optional[str]
    subscribe: int
    language: Optional[str]
    subscribe_time: Optional[int]
    created_at: datetime

class Token(SQLModel):
    access_token: str
    token_type: str

class WechatTokenRequest(SQLModel):
    openid: str

class FileUploadResponse(SQLModel):
    filename: str
    file_path: str
    file_size: int
    upload_time: datetime

# 数据库连接
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# 微信API相关函数
async def get_wechat_access_token() -> str:
    """获取微信access_token，带缓存机制"""
    global wechat_access_token_cache
    
    # 检查缓存是否有效（提前5分钟刷新）
    if (wechat_access_token_cache["token"] and 
        wechat_access_token_cache["expires_at"] and
        datetime.utcnow() < wechat_access_token_cache["expires_at"] - timedelta(minutes=5)):
        return wechat_access_token_cache["token"]
    
    # 获取新的access_token
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WECHAT_APP_ID}&secret={WECHAT_APP_SECRET}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        
        if "access_token" in data:
            wechat_access_token_cache["token"] = data["access_token"]
            wechat_access_token_cache["expires_at"] = datetime.utcnow() + timedelta(seconds=data["expires_in"])
            return data["access_token"]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取微信access_token失败: {data.get('errmsg', '未知错误')}"
            )

async def get_wechat_user_info(openid: str) -> dict:
    """根据openid获取微信用户信息"""
    access_token = await get_wechat_access_token()
    url = f"https://api.weixin.qq.com/cgi-bin/user/info?access_token={access_token}&openid={openid}&lang=zh_CN"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        
        if "errcode" in data and data["errcode"] != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"获取用户信息失败: {data.get('errmsg', '未知错误')}"
            )
        
        return data

def save_or_update_wechat_user(session: Session, user_info: dict) -> WechatUser:
    """保存或更新微信用户信息到数据库"""
    openid = user_info.get("openid")
    
    # 使用原生SQL查询
    result = session.exec(select(WechatUser).where(WechatUser.openid == openid)).first()
    
    if result:
        # 更新现有用户
        result.unionid = user_info.get("unionid")
        result.subscribe = user_info.get("subscribe", 0)
        result.language = user_info.get("language", "zh_CN")
        result.subscribe_time = user_info.get("subscribe_time")
        result.remark = user_info.get("remark")
        result.groupid = user_info.get("groupid")
        result.subscribe_scene = user_info.get("subscribe_scene")
        result.qr_scene = user_info.get("qr_scene")
        result.qr_scene_str = user_info.get("qr_scene_str")
        result.updated_at = datetime.utcnow()
        
        session.add(result)
        session.commit()
        session.refresh(result)
        return result
    else:
        # 创建新用户
        new_user = WechatUser(
            openid=openid,
            unionid=user_info.get("unionid"),
            subscribe=user_info.get("subscribe", 0),
            language=user_info.get("language", "zh_CN"),
            subscribe_time=user_info.get("subscribe_time"),
            remark=user_info.get("remark"),
            groupid=user_info.get("groupid"),
            subscribe_scene=user_info.get("subscribe_scene"),
            qr_scene=user_info.get("qr_scene"),
            qr_scene_str=user_info.get("qr_scene_str")
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    create_db_and_tables()
    yield
    # 关闭时的清理工作

# FastAPI应用
app = FastAPI(
    title="微信服务号后端API",
    description="基于FastAPI的微信服务号后端，支持openid认证和用户信息管理",
    version="1.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

# 中间件配置
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT认证
security = HTTPBearer()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        openid: str = payload.get("sub")
        if openid is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = session.exec(select(WechatUser).where(WechatUser.openid == openid)).first()
    if user is None:
        raise credentials_exception
    return user

# 路由
@app.get("/")
async def root():
    return {"message": "微信服务号后端服务"}

# 微信相关路由
@app.post("/wechat/auth", response_model=Token)
async def wechat_auth(request: WechatTokenRequest, session: Session = Depends(get_session)):
    """根据openid获取用户信息并签发token"""
    try:
        # 获取微信用户信息
        user_info = await get_wechat_user_info(request.openid)
        
        # 检查用户是否关注了公众号
        if user_info.get("subscribe", 0) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户未关注公众号"
            )
        
        # 保存或更新用户信息到数据库
        wechat_user = save_or_update_wechat_user(session, user_info)
        
        # 签发JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": wechat_user.openid}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"认证失败: {str(e)}"
        )

@app.get("/wechat/user/me", response_model=WechatUserResponse)
async def get_current_wechat_user(current_user: WechatUser = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@app.get("/wechat/user/{openid}", response_model=WechatUserResponse)
async def get_wechat_user_by_openid(
    openid: str, 
    session: Session = Depends(get_session),
    current_user: WechatUser = Depends(get_current_user)
):
    """根据openid获取用户信息"""
    user = session.exec(select(WechatUser).where(WechatUser.openid == openid)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

@app.post("/wechat/user/refresh")
async def refresh_wechat_user_info(
    session: Session = Depends(get_session),
    current_user: WechatUser = Depends(get_current_user)
):
    """刷新当前用户的微信信息"""
    try:
        # 重新获取微信用户信息
        user_info = await get_wechat_user_info(current_user.openid)
        
        # 更新数据库中的用户信息
        updated_user = save_or_update_wechat_user(session, user_info)
        
        return {"message": "用户信息刷新成功", "user": updated_user}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新用户信息失败: {str(e)}"
        )

@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, session: Session = Depends(get_session)):
    # 检查用户是否已存在
    existing_user = session.exec(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或邮箱已存在"
        )
    
    # 创建新用户
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return db_user

@app.post("/login", response_model=Token)
async def login(username: str, password: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == username)).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users

@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # 生成唯一文件名
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = Path(UPLOAD_DIR) / unique_filename
    
    # 异步保存文件
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return FileUploadResponse(
        filename=file.filename,
        file_path=str(file_path),
        file_size=len(content),
        upload_time=datetime.utcnow()
    )

@app.post("/upload/multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    uploaded_files = []
    
    for file in files:
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = Path(UPLOAD_DIR) / unique_filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        uploaded_files.append({
            "filename": file.filename,
            "file_path": str(file_path),
            "file_size": len(content)
        })
    
    return {
        "message": f"成功上传 {len(files)} 个文件",
        "files": uploaded_files,
        "upload_time": datetime.utcnow()
    }

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        workers=1,
        loop="uvloop",
        http="httptools",
        access_log=True
    )

# 新增用户详细信息模型
class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profiles"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    openid: str = Field(unique=True, index=True)
    name: str = Field(index=True)
    gender: str
    birth_date: datetime
    height: int
    weight: int
    region: str
    occupation: str
    income: str
    education: str
    religion: Optional[str] = Field(default=None)
    mbti: Optional[str] = Field(default=None)
    phone: str = Field(index=True)
    bio: Optional[str] = Field(default=None)
    private_bio: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserProfileCreate(SQLModel):
    name: str
    gender: str
    birth_date: datetime
    height: int
    weight: int
    region: str
    occupation: str
    income: str
    education: str
    religion: Optional[str] = None
    mbti: Optional[str] = None
    phone: str
    bio: Optional[str] = None
    private_bio: Optional[str] = None

class UserProfileResponse(SQLModel):
    id: int
    name: str
    gender: str
    birth_date: datetime
    height: int
    weight: int
    region: str
    occupation: str
    income: str
    education: str
    religion: Optional[str]
    mbti: Optional[str]
    phone: str
    bio: Optional[str]
    created_at: datetime

# LRU缓存用于人员信息查询
@lru_cache(maxsize=1000)
def get_cached_user_profiles():
    """缓存的用户资料查询"""
    with Session(engine) as session:
        profiles = session.exec(select(UserProfile)).all()
        return [UserProfileResponse.model_validate(profile) for profile in profiles]

def clear_user_profiles_cache():
    """清除用户资料缓存"""
    get_cached_user_profiles.cache_clear()

# 用户资料相关路由
@app.post("/profile", response_model=UserProfileResponse)
async def create_user_profile(
    profile: UserProfileCreate,
    session: Session = Depends(get_session),
    current_user: WechatUser = Depends(get_current_user)
):
    """创建或更新用户资料"""
    # 检查是否已存在资料
    existing_profile = session.exec(
        select(UserProfile).where(UserProfile.openid == current_user.openid)
    ).first()
    
    if existing_profile:
        # 更新现有资料
        for field, value in profile.model_dump().items():
            setattr(existing_profile, field, value)
        existing_profile.updated_at = datetime.utcnow()
        session.add(existing_profile)
        session.commit()
        session.refresh(existing_profile)
        
        # 清除缓存
        clear_user_profiles_cache()
        
        return existing_profile
    else:
        # 创建新资料
        new_profile = UserProfile(
            openid=current_user.openid,
            **profile.model_dump()
        )
        session.add(new_profile)
        session.commit()
        session.refresh(new_profile)
        
        # 清除缓存
        clear_user_profiles_cache()
        
        return new_profile

@app.get("/profiles", response_model=List[UserProfileResponse])
async def get_all_user_profiles(
    current_user: WechatUser = Depends(get_current_user)
):
    """获取所有用户资料（带缓存）"""
    return get_cached_user_profiles()

@app.get("/profile/me", response_model=UserProfileResponse)
async def get_my_profile(
    session: Session = Depends(get_session),
    current_user: WechatUser = Depends(get_current_user)
):
    """获取当前用户资料"""
    profile = session.exec(
        select(UserProfile).where(UserProfile.openid == current_user.openid)
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户资料不存在"
        )
    
    return profile

@app.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileCreate,
    session: Session = Depends(get_session),
    current_user: WechatUser = Depends(get_current_user)
):
    """更新用户资料"""
    profile = session.exec(
        select(UserProfile).where(UserProfile.openid == current_user.openid)
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户资料不存在"
        )
    
    # 更新资料
    for field, value in profile_update.model_dump().items():
        setattr(profile, field, value)
    profile.updated_at = datetime.utcnow()
    
    session.add(profile)
    session.commit()
    session.refresh(profile)
    
    # 清除缓存
    clear_user_profiles_cache()
    
    return profile