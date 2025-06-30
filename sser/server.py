from fastapi import FastAPI, Request, HTTPException, Response, UploadFile, File, Depends, Header
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache.decorator import cache
from pathlib import Path
import requests
import uvicorn
import hashlib
import hmac
import jwt
import os
import uuid
import asyncio
import random
import time
import string
from sqlalchemy import event, func
from sqlalchemy.sql import text
from sqlalchemy import delete
from sqlmodel import SQLModel, Field, create_engine, Session, select
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, field_validator
from typing import Optional

UPLOAD_DIR = "./public/avatar/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

UPLOAD_PHOTO_DIR = "./img/photo/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

beijing_tz = timezone(timedelta(hours=8))
app = FastAPI()
app.mount("/avatars", StaticFiles(directory=UPLOAD_DIR), name="avatars")

# JWT配置
JWT_SECRET = "81efd3fc-4a88-4314-9794-3c8db7004f4b"  # 替换为强密钥
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24 * 7  # 7天有效期

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

# 数据库模型
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    openid: str = Field(primary_key=True)
    nickname: Optional[str] = Field(max_length=10)
    gender: str
    birth_date: datetime
    height: int = Field(default=None)
    weight: float = Field(default=None)
    region_code: str = Field(default=None)
    occupation: str = Field(default=None)
    income_level: str = Field(default=None)
    education: str = Field(default=None)
    religion: str = Field(default=None)
    mbti: str = Field(default=None)
    phone: str = Field(default=None)
    mem: str = Field(default=None)
    mem_pri: str = Field(default=None)
    avatar: str = Field(default=None)
    photo: str = Field(default=None)
    first_photo: str = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(beijing_tz))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(beijing_tz),
        sa_column_kwargs={"onupdate": lambda: datetime.now(beijing_tz)}
    )

# 数据库连接
DATABASE_URL = "mysql+pymysql://root:1234%40Qazx@localhost/cj"
# DATABASE_URL = "mysql+pymysql://root:1234%40Qazx@localhost/cj?charset=utf8mb4&time_zone=%2B08:00"
# DATABASE_URL = "mysql+pymysql://root:1234%40Qazx@localhost/cj?charset=utf8mb4&local_infile=1&timezone=+08:00"
engine = create_engine(DATABASE_URL)
@event.listens_for(engine, "connect")
def set_time_zone(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    try:
        # 设置会话时区为东八区
        cursor.execute("SET time_zone = '+08:00';")
    finally:
        cursor.close()
# 用户资料模型
class ProfileData(BaseModel):
    gender: str
    birth_date: datetime
    nickname: Optional[str] = Field(None, max_length=10)
    height: Optional[int] = None
    weight: Optional[float] = None
    region_code: Optional[str] = None
    occupation: Optional[str] = None
    income_level: Optional[str] = None
    education: Optional[str] = None
    religion: Optional[str] = None
    mbti: Optional[str] = None
    phone: Optional[str] = None
    mem: Optional[str] = None
    mem_pri: Optional[str] = None
    # 添加格式验证器确保兼容性
    @field_validator('birth_date', mode='before')
    def parse_birth_date(cls, value):
        if isinstance(value, str):
            try:
                # 尝试解析 ISO 格式
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                # 兼容旧格式
                return datetime.strptime(value, "%Y-%m-%d")
        return value
    # JWT工具函数
def create_jwt_token(openid: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": openid,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token 已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="无效的 Token")

# 依赖项：验证JWT并获取openid
async def get_current_user(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少认证信息")

    token = authorization.split(" ")[1]
    payload = decode_jwt_token(token)
    return payload.get("sub")

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
    # 生成JWT
    token = create_jwt_token(openid)
    redirect_url = f"http://localhost:5173/auth-success?token={token}"
    #redirect_url = f"http://www.tianshunchenjie.com/auth-success?token={token}"
    print(f"Redirecting to: {redirect_url}")
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

@app.get("/gettime")
async def get_current_time():
    current_time = datetime.now(beijing_tz)
    return {
        "current_time": current_time.isoformat(),
        "timezone": "UTC+8"
    }

@app.get("/wechat/jssdk-signature")
async def get_jssdk_signature(
    url: str,  # 前端传递的当前页面URL
    openid: str = Depends(get_current_user)  # 可选，根据业务需求
):
    """
    生成微信JS-SDK签名
    """
    # 1. 获取access_token
    token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WECHAT_CONFIG['appid']}&secret={WECHAT_CONFIG['secret']}"
    token_resp = requests.get(token_url)
    token_data = token_resp.json()

    if "access_token" not in token_data:
        raise HTTPException(status_code=500, detail="获取access_token失败")

    access_token = token_data["access_token"]

    # 2. 获取jsapi_ticket
    ticket_url = f"https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={access_token}&type=jsapi"
    ticket_resp = requests.get(ticket_url)
    ticket_data = ticket_resp.json()

    if ticket_data.get("errcode") != 0:
        raise HTTPException(status_code=500, detail="获取jsapi_ticket失败")

    jsapi_ticket = ticket_data["ticket"]

    # 3. 生成签名
    noncestr = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    timestamp = str(int(time.time()))

    # 注意：URL必须与前端页面完全一致
    signature_str = f"jsapi_ticket={jsapi_ticket}&noncestr={noncestr}&timestamp={timestamp}&url={url}"

    # 计算签名
    signature = hashlib.sha1(signature_str.encode('utf-8')).hexdigest()

    return {
        "appId": WECHAT_CONFIG['appid'],
        "timestamp": timestamp,
        "nonceStr": noncestr,
        "signature": signature
    }

@app.get("/newcomers")
# @cache(expire=60)  # Cache for 1 minute to reduce database load
async def get_newcomers():
    """
    Get the 10 newest users ordered by created_at (descending)
    Returns: {
        "newcomers": [list of user profiles],
        "count": total number of newcomers
    }
    """
    with Session(engine) as session:
        try:
            # Query the 10 newest users
            stmt = (
                select(User)
                .order_by(User.created_at.desc())
                .limit(10)
            )

            newcomers = session.exec(stmt).all()

            # Get total count of users - 使用正确的 SQLAlchemy 2.0 方式
            count_stmt = select(func.count(User.id))
            total_count = session.scalar(count_stmt)  # 使用 session.scalar() 而不是 exec()

            # Convert to list of dictionaries, excluding sensitive fields
            newcomers_list = []
            for user in newcomers:
                user_data = user.model_dump(
                    exclude={"openid", "mem_pri", "phone"}
                )
                # Ensure we only show first photo to non-matched users
                if user_data.get("photo"):
                    user_data["photo"] = user.first_photo if user.first_photo else ""
                newcomers_list.append(user_data)

            return {
                "newcomers": newcomers_list,
                "count": total_count
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch newcomers: {str(e)}"
            )

# 新增照片上传接口
@app.post("/upload-photo")
async def upload_photo(
    file: UploadFile = File(...),
    openid: str = Depends(get_current_user)
):
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只能上传图片文件")

    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.jpg"
    file_path = os.path.join(UPLOAD_PHOTO_DIR, unique_filename)

    # 保存文件并检查大小
    file_size = 0
    CHUNK_SIZE = 64 * 1024  # 64KB
    try:
        with open(file_path, "wb") as f:
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > 5 * 1024 * 1024:  # 5MB
                    os.remove(file_path)
                    raise HTTPException(status_code=400, detail="图片大小不能超过5MB")
                f.write(chunk)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

    # 异步压缩图片
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, compress_image, file_path)
    except Exception as e:
        print(f"图片压缩失败: {str(e)}")

    return {"filename": unique_filename}

# 新增照片删除接口
class DeletePhotoRequest(BaseModel):
    photo_name: str

@app.post("/delete-photo")
async def delete_photo(
    request: DeletePhotoRequest,
    openid: str = Depends(get_current_user)
):
    # 添加日志记录接收到的请求
    print(f"Deleting photo: {request.photo_name} for user: {openid}")

    # 安全检查
    if not request.photo_name or any(c in request.photo_name for c in ['/', '\\', '..']):
        raise HTTPException(status_code=400, detail="无效的文件名")

    file_path = os.path.join(UPLOAD_PHOTO_DIR, request.photo_name)

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="照片不存在")

    # 数据库操作
    with Session(engine) as session:
        user = session.exec(select(User).where(User.openid == openid)).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 更新照片列表
        photos = [p for p in user.photo.split(',') if p] if user.photo else []
        if request.photo_name in photos:
            photos.remove(request.photo_name)
            user.photo = ','.join(photos)
            session.add(user)
            session.commit()

    # 删除文件
    try:
        os.remove(file_path)
        return {"status": "success", "message": "照片删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")

# 新增保存照片列表接口
@app.post("/save-photos")
async def save_photos(
    photos_data: dict,
    openid: str = Depends(get_current_user)
):
    photos_list = photos_data.get("photos", [])
    photos_str = ','.join(photos_list)

    with Session(engine) as session:
        user = session.exec(select(User).where(User.openid == openid)).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 清理不再使用的照片
        old_photos = user.photo.split(',') if user.photo else []
        for old_photo in old_photos:
            if old_photo and old_photo not in photos_list:
                old_path = os.path.join(UPLOAD_PHOTO_DIR, old_photo)
                try:
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except Exception as e:
                    print(f"警告: 无法删除旧照片 {old_photo}: {str(e)}")

        # 更新照片列表
        user.photo = photos_str
        user.first_photo = photos_list[0] if photos_list else None
        session.add(user)
        session.commit()

    return {"status": "success", "message": "照片列表保存成功"}

# 图片压缩函数
def compress_image(file_path):
    try:
        from PIL import Image
        img = Image.open(file_path)

        # 设置最大尺寸
        max_size = 800
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # 设置质量参数
        quality = 80

        # 如果是PNG且尺寸较大，转换为JPG
        if file_path.lower().endswith('.png') and max(img.size) > 500:
            output_path = os.path.splitext(file_path)[0] + '.jpg'
            img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=quality)
            os.remove(file_path)  # 删除原PNG文件
            return output_path

        # 保存压缩后的图片
        img.save(file_path, quality=quality)
        return file_path
    except Exception as e:
        print(f"图片压缩失败: {str(e)}")
        return file_path


# 在User模型后添加UserLike模型
class UserLike(SQLModel, table=True):
    __tablename__ = "user_likes"
    liker_id: int = Field(primary_key=True, foreign_key="user.id")
    liked_id: int = Field(primary_key=True, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(beijing_tz))

# 点赞请求模型
class LikeRequest(BaseModel):
    liked_id: int
    action: str  # "like" or "unlike"

# 极致优化的点赞处理路由
@app.post("/like")
async def handle_like(
    like_request: LikeRequest,
    openid: str = Depends(get_current_user)
):
    with Session(engine) as session:
        # 1. 获取当前用户ID（修正查询方式）
        stmt = select(User.id).where(User.openid == openid)
        current_user_id = session.exec(stmt).first()

        if current_user_id is None:
            raise HTTPException(status_code=404, detail="用户不存在")

        liker_id = current_user_id
        liked_id = like_request.liked_id

        # 2. 处理点赞操作
        if like_request.action == "like":
            try:
                # 尝试插入点赞记录
                new_like = UserLike(
                    liker_id=liker_id,
                    liked_id=liked_id
                )
                session.add(new_like)
                session.commit()
                return {"status": "success", "message": "点赞成功"}
            except Exception as e:
                # 处理唯一约束冲突（已点赞的情况）
                session.rollback()
                return {"status": "success", "message": "已点赞"}

        elif like_request.action == "unlike":
            # 执行取消点赞操作
            result = session.exec(
                delete(UserLike).where(
                    UserLike.liker_id == liker_id,
                    UserLike.liked_id == liked_id
                )
            )
            session.commit()
            return {"status": "success", "message": "取消点赞成功"}


@app.get("/get-likes")
async def get_likes(
    openid: str = Depends(get_current_user)
):
    with Session(engine) as session:
        # 1. 根据openid获取当前用户ID
        stmt = select(User.id).where(User.openid == openid)
        current_user = session.exec(stmt).first()

        if not current_user:
            raise HTTPException(status_code=404, detail="用户不存在")

        current_user_id = current_user

        # 2. 分别查询 ilike 和 likeme
        # 查询 ilike (我喜欢的)
        ilike_stmt = select(
            UserLike.liked_id.label("user_id"),
            UserLike.created_at
        ).where(UserLike.liker_id == current_user_id)

        ilike_results = session.exec(ilike_stmt).all()

        # 查询 likeme (喜欢我的)
        likeme_stmt = select(
            UserLike.liker_id.label("user_id"),
            UserLike.created_at
        ).where(UserLike.liked_id == current_user_id)

        likeme_results = session.exec(likeme_stmt).all()

        # 3. 处理结果
        ilike = [{
            "user_id": row.user_id,
            "created_at": row.created_at.isoformat()
        } for row in ilike_results]

        likeme = [{
            "user_id": row.user_id,
            "created_at": row.created_at.isoformat()
        } for row in likeme_results]

        return {
            "ilike": ilike,
            "likeme": likeme
        }

# 新增保存资料接口
@app.post("/profile")
async def add_profile(
    profile_data: ProfileData,
    openid: str = Depends(get_current_user)
):
    # 检查用户是否存在
    with Session(engine) as session:
        user = session.exec(select(User).where(User.openid == openid)).first()
        print('user:',user)
        if not user:
            # 创建新用户
            user = User(
                openid=openid,
                **profile_data.model_dump()  # 直接使用转换后的数据
            )
            session.add(user)
        else:
            # 更新现有用户
            for key, value in profile_data.model_dump().items():
                setattr(user, key, value)

        session.commit()

    return {"status": "success", "message": "资料保存成功"}

@app.get("/getlasttime")
async def get_last_time():
    """
    获取cj.user表中最大的updated_at时间戳
    返回格式: { "lasttime": "2023-01-01T00:00:00" } 或 { "lasttime": null }
    """
    with Session(engine) as session:
        try:
            # 高效查询 (使用数据库索引)
            stmt = select(func.max(User.updated_at).label("max_time"))
            result = session.execute(stmt).scalar_one_or_none()

            return {
                "lasttime": result.isoformat() if result else None
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"查询最新时间失败: {str(e)}"
            )


@app.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    openid: str = Depends(get_current_user)
):
    # 验证文件类型
    content_type = file.content_type
    if not content_type or not content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只能上传图片文件")

    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1].lower()  # 获取扩展名并转为小写
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # 保存文件并检查大小
    file_size = 0
    CHUNK_SIZE = 64 * 1024  # 64KB
    try:
        with open(file_path, "wb") as f:
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > 5 * 1024 * 1024:  # 5MB
                    os.remove(file_path)  # 删除部分写入的文件
                    raise HTTPException(status_code=400, detail="图片大小不能超过5MB")
                f.write(chunk)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

    # 更新用户头像
    old_avatar = None
    try:
        with Session(engine) as session:
            user = session.exec(select(User).where(User.openid == openid)).first()
            if not user:
                os.remove(file_path)
                raise HTTPException(status_code=404, detail="用户不存在")

            # 记录旧头像
            old_avatar = user.avatar

            # 更新为新头像
            user.avatar = unique_filename
            session.add(user)
            session.commit()
    except Exception as e:
        # 数据库操作失败时删除新上传的文件
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"数据库更新失败: {str(e)}")

    # 成功更新后删除旧头像
    if old_avatar:
        old_path = os.path.join(UPLOAD_DIR, old_avatar)
        # print(f"尝试删除旧头像: {old_path}")
        try:
            if os.path.exists(old_path) and os.path.isfile(old_path):
                os.remove(old_path)
        except Exception as e:
            # 删除失败不影响主要操作，但应记录日志
            print(f"警告: 无法删除旧头像 {old_avatar}: {str(e)}")

    # 返回头像URL
    avatar_url = f"/avatars/{unique_filename}"
    return {"avatar_url": avatar_url}

class NicknameUpdate(BaseModel):
    nickname: str

# 更新昵称接口
@app.post("/update-nickname")
async def update_nickname(
    update_data: NicknameUpdate,  # 改为接收JSON对象
    openid: str = Depends(get_current_user)
):
    nickname = update_data.nickname
    # 验证昵称长度
    if len(nickname) > 10:
        raise HTTPException(status_code=400, detail="昵称长度不能超过10个字符")

    with Session(engine) as session:
        user = session.exec(select(User).where(User.openid == openid)).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        user.nickname = nickname
        session.add(user)
        session.commit()

    return {"status": "success", "message": "昵称更新成功"}

@app.get("/getprofile")
async def get_profile(
    openid: str = Depends(get_current_user)
):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.openid == openid)).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户资料未找到")
        return user.model_dump(exclude={"openid"})

# 新增管理功能所需的模型
class UserStatus(SQLModel, table=True):
    __tablename__ = "user_status"
    id: int = Field(primary_key=True, foreign_key="user.id")
    state: int = Field(default=1)  # 0:禁用, 1:正常
    expire_at: Optional[datetime] = Field(default=None)

class UserTop(SQLModel, table=True):
    __tablename__ = "user_top"
    id: int = Field(primary_key=True, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(beijing_tz))

# 用户管理响应模型
class AdminUserResponse(BaseModel):
    id: int
    nickname: Optional[str]
    gender: str
    avatar: Optional[str]
    like_count: int
    is_top: bool

# 更新用户状态请求模型
class UpdateUserStatusRequest(BaseModel):
    is_active: bool

# 管理员工具函数
def is_admin(openid: str) -> bool:
    # 这里实现您的管理员验证逻辑
    # 例如：检查openid是否在管理员列表中
    ADMIN_LIST = ["oagEzvlgS2fE90_gROtw9XcH0ELU"]  # 替换为实际的管理员openid
    return openid in ADMIN_LIST

# 管理员依赖项
async def get_admin_user(authorization: str = Header(...)) -> str:
    openid = await get_current_user(authorization)
    if not is_admin(openid):
        raise HTTPException(status_code=403, detail="无管理权限")
    return openid

# 获取用户列表（带点赞数和状态）
@app.get("/admin/users", response_model=list[AdminUserResponse])
async def get_users_with_likes(
    openid: str = Depends(get_admin_user),
    gender: Optional[str] = None
):
    with Session(engine) as session:
        # 构建基础SQL查询
        sql = """
        SELECT 
            u.id,
            u.nickname,
            u.gender,
            u.avatar,
            COUNT(ul.liked_id) AS like_count,
            us.state,
            ut.id IS NOT NULL AS is_top,
            us.expire_at
        FROM 
            user u
        LEFT JOIN 
            user_likes ul ON u.id = ul.liked_id
        LEFT JOIN 
            user_status us ON u.id = us.id
        LEFT JOIN 
            user_top ut ON u.id = ut.id
        {where_clause}
        GROUP BY 
            u.id, u.nickname, u.gender, u.avatar, us.state, ut.id, us.expire_at
        ORDER BY 
            like_count DESC
        """.format(
            where_clause="WHERE u.gender = :gender" if gender else ""
        )

        # 执行查询
        params = {"gender": gender} if gender else {}
        result = session.execute(text(sql), params)
        rows = result.mappings().all()  # 获取字典形式的结果

        # 处理结果
        users = []
        for row in rows:
            is_active = bool(row['state']) and (
                not row['expire_at'] or row['expire_at'] > datetime.now(beijing_tz)
            )
            users.append({
                "id": row['id'],
                "nickname": row['nickname'],
                "gender": row['gender'],
                "avatar": row['avatar'],
                "like_count": row['like_count'],
                "is_active": is_active,
                "is_top": bool(row['is_top'])
            })

        return users

@app.post("/admin/users/{user_id}/status")
async def update_user_active_status(
    user_id: int,
    request: UpdateUserStatusRequest,
    openid: str = Depends(get_admin_user)
):
    with Session(engine) as session:
        stmt = (
            update(UserStatus)
            .where(UserStatus.id == user_id)
            .values(state=int(request.is_active))
        )
        session.exec(stmt)
        session.commit()

    return {"status": "success", "message": "用户状态已更新"}

@app.get("/user/{user_id}")
async def get_user_by_id(
    user_id: int,
    openid: str = Depends(get_current_user)
):
    with Session(engine) as session:
        try:
            # 1. 一次性获取当前用户ID和目标用户信息
            # 查询当前用户ID
            current_user_id_result = session.execute(
                select(User.id).where(User.openid == openid)
            ).first()

            if not current_user_id_result:
                raise HTTPException(status_code=404, detail="当前用户未找到")

            current_user_id = current_user_id_result[0]

            # 查询目标用户信息
            target_user = session.exec(
                select(User).where(User.id == user_id)
            ).first()

            if not target_user:
                raise HTTPException(status_code=404, detail="目标用户未找到")

            # 2. 检查双方喜欢状态（使用单个查询）
            like_query = text("""
                SELECT
                    (SELECT COUNT(*) FROM user_likes
                     WHERE liker_id = :current_id AND liked_id = :target_id) AS i_liked,
                    (SELECT COUNT(*) FROM user_likes
                     WHERE liker_id = :target_id AND liked_id = :current_id) AS they_liked
            """)

            like_result = session.execute(like_query, {
                "current_id": current_user_id,
                "target_id": user_id
            }).fetchone()

            # 3. 准备返回数据
            user_data = target_user.model_dump(
                exclude={"openid", "mem_pri", "phone"}
            )

            # 4. 添加喜欢状态信息
            user_data["i_liked"] = like_result.i_liked > 0
            user_data["they_liked"] = like_result.they_liked > 0

            # 5. 处理照片字段
            if current_user_id == user_id or (user_data["i_liked"] and user_data["they_liked"]):
                # 返回完整照片列表
                user_data["photo"] = target_user.photo
            else:
                # 只返回第一张照片
                user_data["photo"] = target_user.first_photo if target_user.first_photo else ""

            return user_data

        except Exception as e:
            print(f"获取用户详情出错: {str(e)}")
            raise HTTPException(status_code=500, detail="服务器内部错误")

@app.get("/explore_people")
async def explore_people():
    with Session(engine) as session:
        try:
            # MySQL兼容的JSON查询
            stmt = text("""
                SELECT
                    IFNULL(
                        (SELECT JSON_ARRAYAGG(
                            JSON_OBJECT(
                                'gender', gender,
                                'birth_date', DATE_FORMAT(birth_date, '%Y-%m-%dT%H:%i:%s'),
                                'height', height,
                                'avatar', avatar,
                                'education', education,
                                'id', id,
                                'income_level', income_level,
                                'mem', mem,
                                'nickname', nickname,
                                'occupation', occupation,
                                'photo', first_photo,
                                'region_code', region_code,
                                'weight', weight
                            )
                        ) FROM user),
                        JSON_ARRAY()
                    ) as people_json,
                    MAX(updated_at) as lasttime
                FROM user
            """)

            result = session.execute(stmt).fetchone()

            return {
                "people": result[0] if result else [],
                "lasttime": result[1].isoformat() if result and result[1] else None
            }

        except Exception as e:
            print(f"Database error: {str(e)}")
            return {
                "people": [],
                "lasttime": None
            }

@app.get("/explore_people_old")
async def explore_people_old():
    # 定义需要查询的字段列表（排除敏感字段）
    selected_fields = [
        User.gender,
        User.birth_date,
        User.height,
        User.weight,
        User.region_code,
        User.occupation,
        User.income_level,
        User.education,
        User.mem,
        User.id,
        User.nickname,
        User.avatar,
        User.photo
    ]


    with Session(engine) as session:
        # 构建查询语句，只选择需要的字段
        stmt = select(*selected_fields)
        results = session.exec(stmt).all()

        # 将结果转换为字典列表
        people_list = []
        for row in results:
            # 将Row对象转换为字典
            person_dict = row._asdict()

            # 转换日期时间为ISO格式字符串
            if 'birth_date' in person_dict and person_dict['birth_date']:
                person_dict['birth_date'] = person_dict['birth_date'].isoformat()

            people_list.append(person_dict)

    return {"people": people_list}

@app.get('/explore_people_updated')
async def get_updated_people(since: str):
    with Session(engine) as session:
        stmt = select(User).where(User.updated_at > since)
        results = session.exec(stmt).all()
        return {
            'people': [dict(u) for u in results],
            'lasttime': max(u.updated_at for u in results)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)