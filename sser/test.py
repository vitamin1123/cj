from fastapi import FastAPI, Request, HTTPException, Query, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import BaseModel as PydanticBaseModel # Alias to avoid conflict if any
from typing import Optional, List
import httpx
import hashlib
import xml.etree.ElementTree as ET
import time
from jose import JWTError, jwt
from datetime import datetime, timedelta, date # Added date for birth_date
import os

# 微信配置 (保持原有)
WECHAT_TOKEN = "your_wechat_token"  # 替换为你的Token
APPID = "your_appid"  # 替换为你的AppID
APPSECRET = "your_appsecret"  # 替换为你的AppSecret

app = FastAPI()

# Database setup
DATABASE_URL = "mysql+pymysql://root:1234@Qazx@localhost:3306/cj"
engine = create_engine(DATABASE_URL, echo=True)

# JWT settings
# 安全起见，密钥应从环境变量中读取，并确保其足够复杂和唯一
SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secure_secret_key_please_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # Token有效期7天

# OAuth2PasswordBearer 实例，tokenUrl指向获取token的路径（如果使用密码流的话）
# 对于微信登录，我们直接在回调中颁发token，所以这里的tokenUrl更多是形式上的
# 但FastAPI的Depends(oauth2_scheme)会用它来提取Bearer Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/wechat/auth") # 指向微信授权回调，虽然它不直接提供密码流token

# SQLModel definitions
class UserBase(SQLModel):
    nickname: Optional[str] = Field(default=None, max_length=10)
    gender: Optional[str] = Field(default=None)
    birth_date: Optional[date] = Field(default=None) # 使用 date 类型
    height: Optional[int] = Field(default=None)
    weight: Optional[float] = Field(default=None)
    region_code: Optional[str] = Field(default=None, max_length=20)
    occupation: Optional[str] = Field(default=None, max_length=50)
    income_level: Optional[str] = Field(default=None)
    education: Optional[str] = Field(default=None)
    religion: Optional[str] = Field(default=None) # 前端做成选项，后端可以是字符串
    mbti: Optional[str] = Field(default=None, max_length=4)
    phone: Optional[str] = Field(default=None, max_length=11, unique=True, index=True) # 手机号唯一且加索引
    mem: Optional[str] = Field(default=None, max_length=200)
    mem_pri: Optional[str] = Field(default=None, max_length=200)
    avatar: Optional[str] = Field(default=None, max_length=255) # 增加长度以防URL过长
    photo: Optional[str] = Field(default=None, max_length=1024) # 增加长度以防URL列表或长URL

class User(UserBase, table=True):
    openid: str = Field(primary_key=True, index=True, max_length=128)
    # id: Optional[int] = Field(default=None) # 根据用户提供的表结构，openid是主键，这个id字段可以移除或明确其用途
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

class UserCreate(UserBase):
    openid: str

class UserRead(UserBase):
    openid: str
    created_at: datetime
    updated_at: datetime

class ProfileUpdate(UserBase):
    # 用户可以更新UserBase中的所有可选字段
    pass

class Token(PydanticBaseModel):
    access_token: str
    token_type: str
    openid: str # 在token响应中也返回openid，方便前端使用

class TokenData(PydanticBaseModel):
    openid: Optional[str] = None

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Dependency to get DB session
def get_session():
    with Session(engine) as session:
        yield session

# Create access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        openid: Optional[str] = payload.get("sub") # 我们将openid存在 "sub" claim中
        if openid is None:
            raise credentials_exception
        token_data = TokenData(openid=openid)
    except JWTError:
        raise credentials_exception
    
    user = session.get(User, token_data.openid)
    if user is None:
        # 如果token有效但用户在数据库中不存在（例如，用户被删除），也视为认证失败
        raise credentials_exception
    return user

# 可以在应用启动时创建表（如果它们还不存在）
@app.on_event("startup")
def on_startup():
    create_db_and_tables()



# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置微信测试号信息
WECHAT_CONFIG = {
    "appid": "wxccbf0238cab0a75c",  # 请替换为您的正式AppID
    "secret": "f50e7a202c919ec681ed82b79598673b",  # 请替换为您的正式AppSecret
    "token_expire": 7200
}

# 微信公众号配置信息（需从测试号管理页面获取）
# WECHAT_TOKEN = "1234" # 由于您提到不再需要token，此行已注释

@app.get("/")
async def verify_wechat(
    signature: Optional[str] = None,  # 改为可选参数
    timestamp: Optional[str] = None,  # 改为可选参数
    nonce: Optional[str] = None,      # 改为可选参数
    echostr: Optional[str] = None,    # 改为可选参数
):
    """
    微信服务器验证接口
    原有的签名校验逻辑已注释掉，因为正式账号通常在微信后台配置URL和Token完成验证。
    如果微信服务器仍会调用此接口进行验证，它现在会直接返回echostr。
    """
    # 1. 将 token、timestamp、nonce 按字典序排序
    # params = sorted([WECHAT_TOKEN, timestamp, nonce])
    
    # 2. 拼接字符串并 SHA1 加密
    # param_str = "".join(params).encode("utf-8")
    # calculated_signature = hashlib.sha1(param_str).hexdigest()
    
    # 3. 校验签名
    # if calculated_signature == signature:
    #     # 必须返回 text/html 格式，否则微信会报 token check fail:cite[2]
    #     return Response(content=echostr, media_type="text/html; charset=utf-8")
    # else:
    #     raise HTTPException(status_code=403, detail="Invalid signature")
    if echostr:
        return Response(content=echostr, media_type="text/html; charset=utf-8")
    return {"message": "WeChat verification endpoint. Signature check is disabled."}

@app.get("/wechat/callback")
async def wechat_callback(code: str, state: str = None):
    """微信授权回调接口"""
    # 验证state
    # if state != EXPECTED_STATE:
    #     raise HTTPException(status_code=403, detail="Invalid state")
    
    # 使用code获取openid
    result = await wechat_auth(code, state)
    openid = result["openid"]
    redirect_url = f"http://localhost:5173/auth-success?openid={openid}"
    return RedirectResponse(url=redirect_url)

@app.get("/wechat/auth")
async def wechat_auth(code: str, state: str = None):
    """前端通过code获取openid"""
    if not code:
        raise HTTPException(status_code=400, detail="缺少授权码")
    
    # 向微信服务器请求access_token
    token_url = (
        f"https://api.weixin.qq.com/sns/oauth2/access_token"
        f"?appid={WECHAT_CONFIG['appid']}"
        f"&secret={WECHAT_CONFIG['secret']}"
        f"&code={code}"
        f"&grant_type=authorization_code"
    )
    
    try:
        resp = requests.get(token_url)
        data = resp.json()
        
        if "openid" not in data:
            raise HTTPException(
                status_code=400,
                detail=f"微信接口错误: {data.get('errmsg', '未知错误')}"
            )
            
        return {
            "openid": data["openid"],
            "expires_in": data.get("expires_in", WECHAT_CONFIG["token_expire"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.api_route("/wechat", methods=["GET", "POST"]) # 同时处理GET和POST
async def wechat_verification(request: Request,
                            signature: Optional[str] = Query(None),
                            timestamp: Optional[str] = Query(None),
                            nonce: Optional[str] = Query(None),
                            echostr: Optional[str] = Query(None) # echostr仅在GET验证时微信会发送
                            ):
    if request.method == "GET":
        if not all([signature, timestamp, nonce, echostr]):
            raise HTTPException(status_code=400, detail="Missing parameters for WeChat verification")
        
        token = WECHAT_TOKEN # 从配置中获取Token
        params_list = sorted([token, timestamp, nonce])
        sha1 = hashlib.sha1()
        sha1.update("".join(params_list).encode('utf-8'))
        hashcode = sha1.hexdigest()

        if hashcode == signature:
            return Response(content=echostr, media_type="text/plain")
        else:
            raise HTTPException(status_code=403, detail="Verification failed")

    elif request.method == "POST":
        body = await request.body()
        xml_data = body.decode('utf-8')
        # 在这里处理接收到的XML消息 (例如：自动回复、事件推送等)
        # 实际生产环境中，这里会有复杂的业务逻辑
        try:
            root = ET.fromstring(xml_data)
            msg_type = root.find("MsgType").text
            to_user_name = root.find("ToUserName").text
            from_user_name = root.find("FromUserName").text
            create_time = int(time.time())

            # 简单回复示例：收到文本消息则回复相同内容
            if msg_type == "text":
                content = root.find("Content").text
                reply = f"""<xml>
                <ToUserName><![CDATA[{from_user_name}]]></ToUserName>
                <FromUserName><![CDATA[{to_user_name}]]></FromUserName>
                <CreateTime>{create_time}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[收到你的消息: {content}]]></Content>
                </xml>"""
                return Response(content=reply, media_type="application/xml")
            # 可以根据msg_type处理其他类型的消息，如图片、语音、事件等
            else:
                # 对于其他未处理的消息类型，可以回复一个通用消息或不回复
                pass # 或者 return Response(content="success", media_type="text/plain") 微信要求回复success或空串

        except Exception as e:
            print(f"Error processing WeChat message: {e}")
            # 即使处理出错，也建议回复 'success' 或空串给微信服务器，避免微信重试
            # raise HTTPException(status_code=500, detail="Error processing WeChat message")
        return Response(content="success", media_type="text/plain") # 默认回复，防止微信重试

    else:
        raise HTTPException(status_code=405, detail="Method Not Allowed")

@app.get("/wechat/auth", response_model=Token)
async def wechat_auth_callback(code: Optional[str] = Query(None),
                               state: Optional[str] = Query(None), # state参数用于防止CSRF攻击，可选
                               session: Session = Depends(get_session)):
    if not code:
        # 如果前端直接访问此接口且没有code，理论上应该由前端引导用户去微信授权
        # 这里可以返回错误，或重定向到授权链接（但后端重定向体验不如前端控制好）
        raise HTTPException(status_code=400, detail="Authorization code is missing.")

    # 1. 使用code获取access_token和openid
    token_url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={APPID}&secret={APPSECRET}&code={code}&grant_type=authorization_code"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(token_url)
            response.raise_for_status() # 如果请求失败则抛出HTTPError
            data = response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Request to WeChat API failed: {exc}")
        except ValueError: # JSONDecodeError
            raise HTTPException(status_code=500, detail="Failed to parse WeChat API response")

    openid = data.get("openid")
    access_token_wechat = data.get("access_token") # 这是微信的access_token，用于获取用户信息，不是我们JWT的token
    refresh_token = data.get("refresh_token")
    # scope = data.get("scope") # 用户授权的作用域

    if not openid:
        raise HTTPException(status_code=500, detail=f"Failed to get openid from WeChat. Response: {data}")

    # 2. (可选) 使用access_token和openid获取用户基本信息 (如果scope为snsapi_userinfo)
    # user_info_url = f"https://api.weixin.qq.com/sns/userinfo?access_token={access_token_wechat}&openid={openid}&lang=zh_CN"
    # async with httpx.AsyncClient() as client:
    #     try:
    #         user_info_response = await client.get(user_info_url)
    #         user_info_response.raise_for_status()
    #         user_info = user_info_response.json()
    #         # nickname = user_info.get("nickname")
    #         # headimgurl = user_info.get("headimgurl")
    #         # ... 其他用户信息
    #     except httpx.RequestError as exc:
    #         # 获取用户信息失败不是关键性错误，可以继续，或者记录日志
    #         print(f"Failed to get user info from WeChat: {exc}")
    #     except ValueError:
    #         print("Failed to parse WeChat user info response")

    # 3. 检查用户是否存在，不存在则创建
    db_user = session.get(User, openid)
    if not db_user:
        db_user = User(openid=openid)
        # 如果获取了微信昵称和头像，可以在这里设置初始值
        # db_user.nickname = nickname 
        # db_user.avatar = headimgurl
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    # 4. 创建JWT access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    jwt_access_token = create_access_token(
        data={"sub": openid}, expires_delta=access_token_expires
    )

    return Token(access_token=jwt_access_token, token_type="bearer", openid=openid)

@app.post("/profile", response_model=UserRead)
async def update_user_profile(profile_data: ProfileUpdate, 
                              current_user: User = Depends(get_current_user),
                              session: Session = Depends(get_session)):
    """
    Create or Update the profile for the currently authenticated user.
    """
    user_data = profile_data.model_dump(exclude_unset=True) # Get only provided fields
    
    for key, value in user_data.items():
        setattr(current_user, key, value)
    
    current_user.updated_at = datetime.utcnow() # Manually update timestamp as onupdate might not trigger for all ORMs/setups with setattr
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user

@app.get("/profile", response_model=UserRead)
async def read_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get the profile of the currently authenticated user.
    """
    return current_user

# Add a simple root endpoint for health check or basic info
@app.get("/")
async def root():
    return {"message": "Welcome to the CJ WeChat Service API"}

if __name__ == "__main__":
    # Make sure to create tables if they don't exist when running directly
    # In a production setup, you might use Alembic for migrations
    # create_db_and_tables() # Moved to on_startup event
    uvicorn.run(app, host="0.0.0.0", port=8000) # Changed port to 8000 as 8080 is common for other services
