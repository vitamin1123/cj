from fastapi import FastAPI, Request, HTTPException, Response, UploadFile, File, Depends, Body ,Header
from fastapi import WebSocket, WebSocketDisconnect, Query, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from pathlib import Path
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import xml.etree.ElementTree as ET
from uuid import uuid4
from fastapi.encoders import jsonable_encoder
from collections import OrderedDict
import requests
import magic
import json
import uvicorn
import hashlib
import hmac
import jwt
import os
import uuid
import asyncio
import random
import logging
from decimal import Decimal
from logging.handlers import RotatingFileHandler
import time
from PIL import Image, UnidentifiedImageError
import string
from urllib.parse import unquote
from sqlalchemy import event, func
from sqlalchemy.sql import text
from sqlalchemy import delete, update, Numeric, Column, DateTime, Text, Boolean
from sqlmodel import SQLModel, Field, create_engine, Session, select, Relationship
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, field_validator, validator
from typing import List, Optional, Dict
import redis.asyncio as redis
from contextlib import asynccontextmanager



UPLOAD_DIR = "./public/avatar/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

UPLOAD_PHOTO_DIR = "./img/photo/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

beijing_tz = timezone(timedelta(hours=8))

# 在文件开头配置日志
def setup_logging():
    # 创建日志目录
    os.makedirs("./logs", exist_ok=True)

    # 创建日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 文件处理器（每天轮转，保留7天）
    file_handler = RotatingFileHandler(
        "./logs/app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=7
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# 初始化日志
logger = setup_logging()

# 在 FastAPI 实例化前定义 lifespan 处理器
@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Application starting up...")
    print("Application starting up...")
    # 初始化缓存（）
    FastAPICache.init(InMemoryBackend())
    # 应用启动时执行数据库初始化
    with Session(engine) as session:
        try:
            # 创建 user_visits 表（如果不存在）


            # 设置自动清理事件（1个月）
            session.execute(text("""
                CREATE EVENT IF NOT EXISTS clean_old_visits
                ON SCHEDULE EVERY 1 HOUR
                DO
                    DELETE FROM user_visits
                    WHERE created_at < NOW() - INTERVAL 1 MONTH;
            """))
            session.execute(text("SET GLOBAL event_scheduler = ON;"))
            session.commit()
        except Exception as e:
            logger.info(f"数据库初始化失败: {str(e)}")
            # 如果事件创建失败，使用后台任务作为备选
            setup_background_cleaner()

    yield  # 应用运行中

    logger.info("Application shutting down...")
    # 应用关闭时可在此添加清理逻辑（可选）
    # pass
#app = FastAPI()
app = FastAPI(lifespan=lifespan)
app.mount("/avatars", StaticFiles(directory=UPLOAD_DIR), name="avatars")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# JWT配置
JWT_SECRET = os.environ.get("JWT_SECRET", "default-fallback-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24 * 7  # 7天有效期
# 微信支付配置（请替换为实际值）
WECHAT_PAY_CONFIG = {
    "mch_id": "1721330145",
    "api_key": "5f7D2c9A0b4E8g3H1j6K7m2n8P9q0R3s",
    "api_v3_key": "8A3b7C9d2E5f1G4h6J0k3L7m9N2p5Q8r",
    "notify_url": "https://www.tianshunchenjie.com/api/payment/notify"
}

ADMIN_OPENID = "oagEzvlgS2fE90_gROtw9XcH0ELU"

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
    "secret": os.environ.get("WECHAT_SECRET", "default-fallback-secret"), #WECHAT_SECRET 请替换为您的正式AppSecret
    "token_expire": 7200
}

class ChatBase(SQLModel):
    user_openid: str = Field(max_length=128, index=True)
    admin_openid: str = Field(
        max_length=128,
        default=ADMIN_OPENID
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP")
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True),
                       server_default="CURRENT_TIMESTAMP",
                       onupdate="CURRENT_TIMESTAMP")
    )

class Chat(ChatBase, table=True):
    __tablename__ = "chats"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_openid: str = Field(max_length=128)
    messages: List["Message"] = Relationship(back_populates="chat")

class MessageBase(SQLModel):
    content: str = Field(sa_column=Column(Text))
    sender_openid: str = Field(max_length=128)
    sent_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP")
    )
    is_read: bool = Field(sa_column=Column(Boolean, default=False))

class Message(MessageBase, table=True):
    __tablename__ = "messages"

    id: str = Field(primary_key=True)
    chat_id: int = Field(foreign_key="chats.id")
    chat: Optional[Chat] = Relationship(back_populates="messages")

# 数据库模型
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    openid: str = Field(max_length=128, unique=True, index=True)
    nickname: Optional[str] = Field(max_length=10)
    gender: str
    birth_date: datetime
    height: int = Field(default=None)
    weight: float = Field(default=None)
    region_code: str = Field(default=None)
    occupation: str = Field(default=None)
    income_level: Optional[Decimal] = Field(default=None, sa_type=Numeric(10, 2))
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
    tip: Optional[Decimal] = Field(default=None, sa_type=Numeric(18, 2))  # 使用直接导入的 Numeric
    istop: int = Field(default=0)  # 是否置顶
    married: int = Field(default=0)  # 婚姻状态
    child: int = Field(default=0)  # 是否有子女
    points: int = Field(default=0, sa_type=Numeric(10, 0))

class UserTmp(SQLModel, table=True):
    __tablename__ = "user_tmp"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), nullable=False)
    openid: str = Field(primary_key=True)
    nickname: Optional[str] = Field(max_length=10)
    gender: str = Field(default=None)
    birth_date: datetime = Field(default=None)
    height: int = Field(default=None)
    weight: float = Field(default=None)
    region_code: str = Field(default=None)
    occupation: str = Field(default=None)
    income_level: Optional[Decimal] = Field(default=None, sa_type=Numeric(10, 2))
    education: str = Field(default=None)
    religion: str = Field(default=None)
    mbti: str = Field(default=None)
    phone: str = Field(default=None)
    mem: str = Field(default=None)
    mem_pri: str = Field(default=None)
    avatar: str = Field(default=None)
    photo: str = Field(default=None)
    first_photo: str = Field(default=None)

    # 新增字段
    state: int = Field(default=0)  # 审核状态
    tip: Optional[Decimal] = Field(default=None, sa_type=Numeric(18, 2))  # 使用直接导入的 Numeric
    istop: int = Field(default=0)  # 是否置顶
    married: int = Field(default=0)  # 婚姻状态
    child: int = Field(default=0)  # 是否有子女

    # 时间戳字段
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(beijing_tz)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(beijing_tz),
        sa_column_kwargs={"onupdate": lambda: datetime.now(beijing_tz)}
    )

class UserPointsLog(SQLModel, table=True):
    __tablename__ = "user_points_log"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    action: str = Field(max_length=20)        # login / recharge / tip / liked / audit
    points: int
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP")
    )

class UserRecharge(SQLModel, table=True):
    __tablename__ = "user_recharge"
    id: Optional[int] = Field(default=None, primary_key=True)
    openid: str = Field(max_length=128)
    amount: Decimal = Field(sa_type=Numeric(10, 2))
    transaction_id: str = Field(max_length=64, unique=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP")
    )

# 数据库连接
DATABASE_URL = "mysql+pymysql://root:12345%40Qazxc@localhost/cj"
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
    income_level: Optional[float] = None
    education: Optional[str] = None
    religion: Optional[str] = None
    mbti: Optional[str] = None
    phone: Optional[str] = None
    mem: Optional[str] = None
    mem_pri: Optional[str] = None
    married: Optional[int] = None
    child: Optional[int] = None
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
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
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

async def get_websocket_user(token: str):
    try:
        payload = decode_jwt_token(token)
        return payload.get("sub")  # 返回openid
    except Exception as e:
        print(f"WebSocket认证失败: {str(e)}")
        return None

# 依赖项：验证JWT并获取openid
async def get_current_user(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少认证信息")

    token = authorization.split(" ")[1]
    payload = decode_jwt_token(token)
    return payload.get("sub")


class ConnectionManager:
    def __init__(self):
        self._redis = None

    async def _get_redis(self) -> redis.Redis:
        if self._redis is None:
            self._redis = redis.from_url("redis://localhost")
        return self._redis
    async def should_allow(self, key: str, window: int = 2) -> bool:
        """
        key:  openid 或 ip
        返回值 True 表示允许，False 表示被限流
        """
        r = await self._get_redis()
        now = int(time.time())
        pipe = r.pipeline()
        pipe.zadd(key, {now: now})              # 记录当前时间戳
        pipe.zremrangebyscore(key, 0, now - window)  # 清理旧窗口
        pipe.zcard(key)                         # 当前窗口内次数
        _, _, count = await pipe.execute()
        return count <= 1
    async def send_to_user(self, openid: str, payload: dict):
        r = await self._get_redis()
        await r.publish(f"user:{openid}", json.dumps(payload))

    async def send_to_admin(self, payload: dict):
        r = await self._get_redis()
        await r.publish("admin", json.dumps(payload))

class RevokeMessageRequest(BaseModel):
    message_id: str

manager = ConnectionManager()

@app.websocket("/ws/user")
# @limiter.limit("1/2second")
async def websocket_user_endpoint(
    websocket: WebSocket,
    token: str = Query(..., alias="token")
):
    openid = await get_websocket_user(token)
    if not openid:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    logger.info(f"用户连接建立: {openid}")

    # 创建 Redis 连接
    r = await manager._get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(f"user:{openid}")

    # 任务1：把 Redis 消息推给前端
    async def redis_to_ws():
        async for msg in pubsub.listen():
            if msg["type"] == "message":
                try:
                    await websocket.send_text(msg["data"].decode())
                except Exception:
                    break

    # 任务2：把前端消息推给 Redis / 业务逻辑
    async def ws_to_redis():
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
                    continue
                # ------------ 限流检查 ------------
                if not await manager.should_allow(openid):
                    await websocket.send_text(
                        json.dumps({"type": "rate_limit", "msg": "发送过快，请 2 秒后再试"})
                    )
                    continue
                message = json.loads(data)
                if not isinstance(message, dict) or "text" not in message:
                    continue

                # 保存消息到数据库
                with Session(engine) as session:
                    chat = session.exec(
                        select(Chat).where(Chat.user_openid == openid).limit(1)
                    ).first()
                    if not chat:
                        chat = Chat(user_openid=openid)
                        session.add(chat)
                        session.commit()
                        session.refresh(chat)

                    new_msg = Message(
                        id=message["id"],
                        chat_id=chat.id,
                        sender_openid=openid,
                        content=message["text"],
                        sent_at=datetime.now(beijing_tz)
                    )
                    session.add(new_msg)
                    session.commit()

                    chat_summary = get_chat_summary_by_chat_id(chat.id)
                    if chat_summary:
                        await manager.send_to_admin({
                            "type": "chat_list_update",
                            "chat": chat_summary
                        })

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"用户消息处理异常: {e}")
                break

    # 并发执行两个协程，任意一个返回即结束
    try:
        await asyncio.gather(redis_to_ws(), ws_to_redis())
    finally:
        await pubsub.unsubscribe(f"user:{openid}")
        await pubsub.close()
        logger.info(f"用户 {openid} 连接清理完成")


# ---------------- /ws/admin ----------------
@app.websocket("/ws/admin")
async def websocket_admin_endpoint(
    websocket: WebSocket,
    token: str = Query(..., alias="token")
):
    openid = await get_websocket_user(token)
    if not is_admin(openid):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    logger.info("管理员连接建立")

    r = await manager._get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe("admin")

    # 任务1：把 Redis 消息推给前端
    async def redis_to_ws():
        async for msg in pubsub.listen():
            if msg["type"] == "message":
                try:
                    await websocket.send_text(msg["data"].decode())
                except Exception:
                    break

    # 任务2：把前端消息推给用户
    async def ws_to_redis():
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
                    continue

                message = json.loads(data)
                if not all(k in message for k in ["chat_id", "text"]):
                    continue

                with Session(engine) as session:
                    chat = session.get(Chat, message["chat_id"])
                    if not chat:
                        continue
                    user_openid = chat.user_openid

                    new_msg = Message(
                        id=message["id"],
                        chat_id=chat.id,
                        sender_openid=ADMIN_OPENID,
                        content=message["text"],
                        sent_at=datetime.now(beijing_tz),
                        is_read=True
                    )
                    session.add(new_msg)
                    session.commit()

                    await manager.send_to_user(user_openid, {
                        "type": "admin_message",
                        "text": message["text"],
                        "chat_id": chat.id,
                        "sender": ADMIN_OPENID,
                        "sent_at": datetime.now(beijing_tz).isoformat()
                    })
            except RateLimitExceeded:
                await websocket.send_text(
                    json.dumps({"type": "rate_limit", "msg": "发送过快，请 3 秒后再试"})
                )
                continue
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"管理员消息处理异常: {e}")
                break

    try:
        await asyncio.gather(redis_to_ws(),  ws_to_redis())
    finally:
        await pubsub.unsubscribe("admin")
        await pubsub.close()
        logger.info("管理员连接清理完成")


async def get_admin_user(authorization: str = Header(...)) -> str:
    openid = await get_current_user(authorization)
    if not is_admin(openid):
        raise HTTPException(status_code=403, detail="无管理权限")
    return openid

# 添加消息撤回接口 - 用户端
@app.post("/user/chat/revoke")
async def revoke_user_message(
    revoke_request: RevokeMessageRequest,
    openid: str = Depends(get_current_user)
):
    """用户撤回自己发送的消息（2分钟内）"""
    with Session(engine) as session:
        try:
            # 找到对应的chat
            chat = session.exec(
                select(Chat).where(Chat.user_openid == openid)
            ).first()
            if not chat:
                raise HTTPException(status_code=404, detail="聊天会话不存在")

            # 找到消息
            message = session.exec(
                select(Message)
                .where(
                    Message.id == revoke_request.message_id,
                    Message.chat_id == chat.id,
                    Message.sender_openid == openid
                )
            ).first()

            if not message:
                raise HTTPException(status_code=404, detail="消息不存在或无权限撤回")

            # 检查是否在2分钟内
            now = datetime.now(beijing_tz)
            sent_at = message.sent_at
            if sent_at.tzinfo is None:
                sent_at = sent_at.replace(tzinfo=beijing_tz)
            if now - sent_at > timedelta(minutes=2):
                raise HTTPException(status_code=400, detail="消息已超过2分钟，无法撤回")

            # 删除消息
            session.delete(message)
            session.commit()

            # 通知管理员端
            await manager.send_to_admin(ADMIN_OPENID, json.dumps({
                "type": "revoke_message",
                "message_id": revoke_request.message_id,
                "chat_id": chat.id
            }))

            return {"status": "success", "message": "消息撤回成功"}

        except Exception as e:
            session.rollback()
            logger.error(f"用户撤回消息失败: {str(e)}")
            raise HTTPException(status_code=500, detail="撤回消息失败")

# 添加消息撤回接口 - 管理员端
@app.post("/admin/chat/revoke")
async def revoke_admin_message(
    revoke_request: RevokeMessageRequest,
    openid: str = Depends(get_admin_user)
):
    """管理员撤回自己发送的消息（2分钟内）"""
    with Session(engine) as session:
        try:
            # 找到消息
            message = session.exec(
                select(Message)
                .where(
                    Message.id == revoke_request.message_id,
                    Message.sender_openid == ADMIN_OPENID
                )
            ).first()

            if not message:
                raise HTTPException(status_code=404, detail="消息不存在或无权限撤回")

            # 检查是否在2分钟内
            now = datetime.now(beijing_tz)
            sent_at = message.sent_at
            if sent_at.tzinfo is None:
                sent_at = sent_at.replace(tzinfo=beijing_tz)
            if now - sent_at > timedelta(minutes=2):
                raise HTTPException(status_code=400, detail="消息已超过2分钟，无法撤回")

            # 获取chat信息
            chat = session.get(Chat, message.chat_id)
            if not chat:
                raise HTTPException(status_code=404, detail="聊天会话不存在")

            # 删除消息
            session.delete(message)
            session.commit()

            # 通知用户端
            await manager.send_to_user(chat.user_openid, json.dumps({
                "type": "revoke_message",
                "message_id": revoke_request.message_id,
                "chat_id": chat.id
            }))

            return {"status": "success", "message": "消息撤回成功"}

        except Exception as e:
            session.rollback()
            logger.error(f"管理员撤回消息失败: {str(e)}")
            raise HTTPException(status_code=500, detail="撤回消息失败")

def get_chat_summary_by_chat_id(chat_id: int) -> dict:
    with Session(engine) as session:
        chat = session.exec(
            select(
                Chat.id,
                Chat.user_openid,
                UserTmp.id.label("user_id"),
                UserTmp.nickname,
                UserTmp.avatar,
                UserTmp.gender
            )
            .join(UserTmp, UserTmp.openid == Chat.user_openid)
            .where(Chat.id == chat_id)
        ).first()

        if not chat:
            return None

        last_message = session.exec(
            select(Message.content, Message.sent_at)
            .where(Message.chat_id == chat_id)
            .order_by(Message.sent_at.desc())
            .limit(1)
        ).first()

        unread_count = session.scalar(
            select(func.count(Message.id))
            .where(
                Message.chat_id == chat_id,
                Message.sender_openid != ADMIN_OPENID,
                Message.is_read == False
            )
        )

        return {
            "chat_id": chat.id,
            "user_id": chat.user_id,
            "user_openid": chat.user_openid,
            "user_nickname": chat.nickname,
            "user_avatar": chat.avatar,
            "user_gender": chat.gender,
            "last_message": last_message[0] if last_message else "",
            "last_message_time": last_message[1].isoformat() if last_message else None,
            "unread_count": unread_count,
            "updated_at": last_message[1].isoformat() if last_message else None
        }

# 获取活跃聊天会话列表
@app.get("/admin/chats")
async def get_active_chats(
    openid: str = Depends(get_admin_user)
):
    """
    获取活跃聊天会话列表（包含最后一条消息和未读消息数）
    """
    with Session(engine) as session:
        try:
            # 查询所有聊天会话及关联的用户信息
            chats = session.exec(
                select(
                    Chat.id,
                    Chat.user_openid,
                    Chat.created_at,
                    Chat.updated_at,
                    UserTmp.id.label("user_id"),
                    UserTmp.nickname,
                    UserTmp.avatar,
                    UserTmp.gender
                )
                .join(UserTmp, UserTmp.openid == Chat.user_openid)
            ).all()

            # 查询每个会话的未读消息数和最后一条消息
            chat_list = []
            for chat in chats:
                # 获取最后一条消息
                last_message = session.exec(
                    select(Message.content, Message.sent_at)
                    .where(Message.chat_id == chat.id)
                    .order_by(Message.sent_at.desc())
                    .limit(1)
                ).first()

                # 获取未读消息数（用户发送且未读的）
                unread_count = session.scalar(
                    select(func.count(Message.id))
                    .where(
                        Message.chat_id == chat.id,
                        Message.sender_openid != ADMIN_OPENID,  # 排除管理员自己的消息
                        Message.is_read == False
                    )
                )

                chat_list.append({
                    "chat_id": chat.id,
                    "user_id": chat.user_id,
                    "user_openid": chat.user_openid,
                    "user_nickname": chat.nickname,
                    "user_avatar": chat.avatar,
                    "user_gender": chat.gender,
                    "last_message": last_message[0] if last_message else "",
                    "last_message_time": last_message[1].isoformat() if last_message else None,
                    "unread_count": unread_count,
                    "updated_at": chat.updated_at.isoformat()
                })

            # 按最后更新时间排序
            chat_list.sort(key=lambda x: x['updated_at'], reverse=True)

            return chat_list

        except Exception as e:
            logger.error(f"获取聊天会话失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="获取聊天会话失败"
            )

@app.get("/user/chat/messages")
async def get_user_chat_history(
    openid: str = Depends(get_current_user)
):
    """
    用户获取与自己相关的聊天记录
    """
    with Session(engine) as session:
        try:
            # 根据 openid 找到 chat
            chat = session.exec(
                select(Chat).where(Chat.user_openid == openid)
            ).first()

            if not chat:
                return []  # 没有聊天记录

            # 查询该 chat 的所有消息
            messages = session.exec(
                select(
                    Message.id,
                    Message.content,
                    Message.sender_openid,
                    Message.sent_at,
                    Message.is_read
                )
                .where(Message.chat_id == chat.id)
                .order_by(Message.sent_at.asc())
            ).all()

            # 格式化
            return [
                {
                    "id": msg.id,
                    "content": msg.content,
                    "is_sent": msg.sender_openid == openid,  # 用户自己发的
                    "sent_at": msg.sent_at.isoformat(),
                    "is_read": msg.is_read
                }
                for msg in messages
            ]

        except Exception as e:
            logger.error(f"用户获取聊天历史失败: {str(e)}")
            raise HTTPException(status_code=500, detail="获取聊天历史失败")

@app.post("/user/chat/mark-read")
async def mark_user_chat_as_read(
    openid: str = Depends(get_current_user)
):
    """
     用户将管理员发送给自己的消息标记为已读
    """
    with Session(engine) as session:
        try:
            chat = session.exec(
                select(Chat).where(Chat.user_openid == openid)
            ).first()
            if not chat:
                return {"status": "success", "message": "无聊天记录"}

            # 只标记管理员发的未读消息
            result = session.exec(
                update(Message)
                .where(
                    Message.chat_id == chat.id,
                    Message.sender_openid == ADMIN_OPENID,
                    Message.is_read == False
                )
                .values(is_read=True)
            )
            session.commit()

            return {"status": "success", "message": f"已标记 {result.rowcount} 条消息为已读"}

        except Exception as e:
            session.rollback()
            logger.error(f"用户标记已读失败: {str(e)}")
            raise HTTPException(status_code=500, detail="标记已读失败")

# 获取聊天历史消息
@app.get("/admin/chats/{chat_id}/messages")
async def get_chat_history(
    chat_id: int,
    openid: str = Depends(get_admin_user)
):
    """
    获取指定聊天的历史消息
    """
    with Session(engine) as session:
        try:
            # 验证聊天会话是否存在
            chat = session.get(Chat, chat_id)
            if not chat:
                raise HTTPException(status_code=404, detail="聊天会话不存在")

            # 查询该聊天的所有消息
            messages = session.exec(
                select(
                    Message.id,
                    Message.content,
                    Message.sender_openid,
                    Message.sent_at,
                    Message.is_read
                )
                .where(Message.chat_id == chat_id)
                .order_by(Message.sent_at.asc())
            ).all()

            # 格式化消息
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "id": msg.id,
                    "content": msg.content,
                    "sender": "admin" if msg.sender_openid == ADMIN_OPENID else "user",
                    "sent_at": msg.sent_at.isoformat(),
                    "is_read": msg.is_read
                })

            return formatted_messages

        except Exception as e:
            logger.error(f"获取聊天历史失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="获取聊天历史失败"
            )

# 标记消息为已读
@app.post("/admin/chats/{chat_id}/mark-read")
async def mark_chat_as_read(
    chat_id: int,
    openid: str = Depends(get_admin_user)
):
    """
    将指定聊天中用户发送的消息标记为已读
    """
    with Session(engine) as session:
        try:
            # 验证聊天会话是否存在
            chat = session.get(Chat, chat_id)
            if not chat:
                raise HTTPException(status_code=404, detail="聊天会话不存在")

            # 更新所有未读消息（用户发送的）为已读
            result = session.exec(
                update(Message)
                .where(
                    Message.chat_id == chat_id,
                    Message.sender_openid != ADMIN_OPENID,  # 只标记用户的消息
                    Message.is_read == False
                )
                .values(is_read=True)
            )
            session.commit()

            return {"status": "success", "message": f"已标记 {result.rowcount} 条消息为已读"}

        except Exception as e:
            session.rollback()
            logger.error(f"标记消息为已读失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="标记消息为已读失败"
            )

# 微信公众号配置信息（需从测试号管理页面获取）
# WECHAT_TOKEN = "1234" # 由于您提到不再需要token，此行已注释
# 打赏请求模型
class TipRequest(BaseModel):
    amount: Decimal
    message: Optional[str] = None

@app.post("/create-tip-payment")
async def create_tip_payment(
    request: TipRequest,
    openid: str = Depends(get_current_user)
):
    """
    创建打赏支付订单（含前端附言）
    """
    amount = request.amount
    message = request.message or "感谢红娘"

    # 金额校验
    if amount <= 0:
        raise HTTPException(status_code=400, detail="打赏金额必须大于0")

    # 生成订单号
    out_trade_no = f"TIP{int(time.time())}{random.randint(1000, 9999)}"
    nonce_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    # 构造统一下单参数
    params = {
        "appid": WECHAT_CONFIG['appid'],
        "mch_id": WECHAT_PAY_CONFIG['mch_id'],
        "nonce_str": nonce_str,
        "body": "打赏",  # ✅ 前端附言
        "out_trade_no": out_trade_no,
        "total_fee": int(amount * 100),  # 分
        "spbill_create_ip": "127.0.0.1",
        "notify_url": WECHAT_PAY_CONFIG['notify_url'].replace('payment/notify', 'tip/notify'),
        "trade_type": "JSAPI",
        "openid": openid,
        "attach": message[:127]
    }

    # 生成签名
    sorted_params = sorted(params.items())
    sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
    sign_str += f"&key={WECHAT_PAY_CONFIG['api_key']}"
    sign = hashlib.md5(sign_str.encode()).hexdigest().upper()
    params['sign'] = sign

    # 构造XML
    xml_data = "<xml>" + "".join([f"<{k}>{v}</{k}>" for k, v in params.items()]) + "</xml>"

    # 发送到微信
    response = requests.post(
        "https://api.mch.weixin.qq.com/pay/unifiedorder",
        data=xml_data.encode('utf-8'),
        headers={'Content-Type': 'application/xml'}
    )

    root = ET.fromstring(response.content)
    result = {child.tag: child.text for child in root}

    if result.get('return_code') != 'SUCCESS' or result.get('result_code') != 'SUCCESS':
        error_msg = result.get('return_msg', result.get('err_code_des', '未知错误'))
        raise HTTPException(status_code=400, detail=f"微信支付下单失败: {error_msg}")

    # 构造前端支付参数
    prepay_id = result['prepay_id']
    timestamp = str(int(time.time()))
    nonce_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    pay_params = {
        "appId": WECHAT_CONFIG['appid'],
        "timeStamp": timestamp,
        "nonceStr": nonce_str,
        "package": f"prepay_id={prepay_id}",
        "signType": "MD5"
    }

    pay_sign_str = "&".join([f"{k}={v}" for k, v in sorted(pay_params.items())])
    pay_sign_str += f"&key={WECHAT_PAY_CONFIG['api_key']}"
    pay_params['paySign'] = hashlib.md5(pay_sign_str.encode()).hexdigest().upper()

    return pay_params
# 打赏支付结果回调
@app.post("/tip/notify")
async def tip_notify(request: Request):
    """
    打赏支付结果回调接口（事务安全版）
    """
    body = await request.body()
    root = ET.fromstring(body)
    result = {child.tag: child.text for child in root}

    # 验证签名
    sign = result.pop('sign', '')
    sorted_params = sorted(result.items())
    sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
    sign_str += f"&key={WECHAT_PAY_CONFIG['api_key']}"
    calculated_sign = hashlib.md5(sign_str.encode()).hexdigest().upper()

    if sign != calculated_sign:
        return Response(
            content="<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[签名失败]]></return_msg></xml>",
            media_type="application/xml"
        )

    if result['return_code'] != 'SUCCESS' or result['result_code'] != 'SUCCESS':
        return Response(
            content="<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[支付失败]]></return_msg></xml>",
            media_type="application/xml"
        )

    openid = result['openid']
    transaction_id = result['transaction_id']
    amount = Decimal(result['total_fee']) / 100
    # print(f"[tip_notify] 原始 result: {result}")

    user_message = result.get('attach', '感谢红娘')[:255]

    try:
        with Session(engine) as session:
            with session.begin():  # ✅ 开启事务
                # 1. 插入打赏记录
                session.execute(
                    text("""
                        INSERT INTO user_tips (openid, amount, message)
                        VALUES (:openid, :amount, :message)
                    """),
                    {"openid": openid, "amount": amount, "message": user_message}
                )

                # 2. 更新 user_tmp
                session.execute(
                    text("""
                        UPDATE user_tmp
                        SET tip = COALESCE(tip, 0) + :amount
                        WHERE openid = :openid
                    """),
                    {"openid": openid, "amount": amount}
                )

                # 3. 更新 user（如果存在）
                session.execute(
                    text("""
                        UPDATE user
                        SET tip = COALESCE(tip, 0) + :amount
                        WHERE openid = :openid
                    """),
                    {"openid": openid, "amount": amount}
                )
                # 4. 给用户加积分：2 × 打赏金额（元）
                session.execute(
                    text("""
                        UPDATE user
                        SET points = COALESCE(points, 0) + :points_add
                        WHERE openid = :openid
                    """),
                    {"openid": openid, "points_add": amount * 2}
                )

            # ✅ 事务自动提交
            logger.info(f"打赏成功：{transaction_id}，金额：{amount}，用户：{openid}，附言：{user_message}")

    except Exception as e:
        logger.error(f"打赏事务失败: {str(e)}")
        return Response(
            content="<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[DB update failed]]></return_msg></xml>",
            media_type="application/xml"
        )

    return Response(
        content="<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>",
        media_type="application/xml"
    )

# 获取打赏记录
@app.get("/tip/history")
async def get_tip_history(
    openid: str = Depends(get_current_user)
):
    """
    获取用户的打赏记录
    """
    with Session(engine) as session:
        try:
            records = session.execute(
                text("""
                    SELECT amount, message, created_at
                    FROM user_tips
                    WHERE openid = :openid
                    ORDER BY created_at DESC
                    LIMIT 50
                """),
                {"openid": openid}
            ).mappings().all()

            return {
                "records": [
                    {
                        "amount": float(record["amount"]),
                        "message": record["message"],
                        "created_at": record["created_at"].isoformat()
                    }
                    for record in records
                ]
            }
        except Exception as e:
            logger.error(f"获取打赏记录失败: {str(e)}")
            raise HTTPException(status_code=500, detail="获取打赏记录失败")

# 获取累计打赏金额
@app.get("/tip/total")
async def get_tip_total(
    openid: str = Depends(get_current_user)
):
    """
    获取用户的累计打赏金额
    """
    with Session(engine) as session:
        try:
            total = session.scalar(
                text("""
                    SELECT COALESCE(SUM(amount), 0)
                    FROM user_tips
                    WHERE openid = :openid
                """),
                {"openid": openid}
            )
            return {"total": float(total)}
        except Exception as e:
            logger.error(f"获取打赏总额失败: {str(e)}")
            raise HTTPException(status_code=500, detail="获取打赏总额失败")



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
    with Session(engine) as session:
        exists = session.exec(
            select(UserTmp).where(UserTmp.openid == openid)
        ).first()
        if not exists:
            session.add(UserTmp(
                openid=openid,
                id=str(uuid4()),
                created_at=datetime.now(beijing_tz),
                updated_at=datetime.now(beijing_tz)
            ))
            session.commit()
    # 生成JWT
    token = create_jwt_token(openid)
    redirect_url = f"http://localhost:5173/auth-success?token={token}"
    # redirect_url = f"https://www.tianshunchenjie.com/auth-success?token={token}"
    logger.info(f"Redirecting to: {redirect_url}")
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
        logger.error(f'/wechat/auth-{str(e)}')
        raise HTTPException(status_code=500, detail="服务器内部错误")

@app.get("/gettime")
async def get_current_time():
    current_time = datetime.now(beijing_tz)
    return {
        "current_time": current_time.isoformat(),
        "timezone": "UTC+8"
    }

@app.get("/wechat/jssdk-signature-1")
async def get_jssdk_signature_1(
    url: str,  # 前端传递的当前页面URL
    openid: str = Depends(get_current_user)
):
    """
    生成微信JS-SDK签名 (iOS兼容版本)
    """
    try:
        # 修复1：iOS需要URL解码后重新编码
        decoded_url = unquote(url)
        # iOS特殊处理：移除重复编码
        clean_url = decoded_url.split("#")[0]

        # 修复2：验证URL格式（iOS严格要求）
        if not clean_url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL format for iOS")

        # 获取access_token
        token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WECHAT_CONFIG['appid']}&secret={WECHAT_CONFIG['secret']}"
        token_resp = requests.get(token_url)
        token_data = token_resp.json()

        if "access_token" not in token_data:
            # iOS特殊日志
            logger.info(f"iOS_WX_Error: {token_data.get('errmsg', '未知错误')}")
            raise HTTPException(status_code=500, detail="获取access_token失败")

        access_token = token_data["access_token"]

        # 获取jsapi_ticket
        ticket_url = f"https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={access_token}&type=jsapi"
        ticket_resp = requests.get(ticket_url)
        ticket_data = ticket_resp.json()

        if ticket_data.get("errcode") != 0:
            # iOS特殊日志
            logger.info(f"iOS_WX_Ticket_Error: {ticket_data.get('errmsg', '未知错误')}")
            raise HTTPException(status_code=500, detail="获取jsapi_ticket失败")

        jsapi_ticket = ticket_data["ticket"]

        # 生成签名
        noncestr = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        timestamp = str(int(time.time()))

        # 修复3：iOS要求参数排序严格
        params = {
            "jsapi_ticket": jsapi_ticket,
            "noncestr": noncestr,
            "timestamp": timestamp,
            "url": clean_url
        }
        param_str = "&".join([f"{k}={params[k]}" for k in sorted(params.keys())])

        # 计算签名
        signature = hashlib.sha1(param_str.encode('utf-8')).hexdigest()

        # iOS调试信息
        logger.info(f"iOS_WX_Sign: url={clean_url}, sig={signature}")

        return {
            "appId": WECHAT_CONFIG['appid'],
            "timestamp": timestamp,
            "nonceStr": noncestr,
            "signature": signature
        }

    except Exception as e:
        # iOS特殊错误处理
        logger.info(f"iOS_WX_Exception: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"iOS签名生成失败"
        )

@app.get("/wechat/jssdk-signature")
async def get_jssdk_signature(
    url: str,  # 前端传递的当前页面URL
    openid: str = Depends(get_current_user)  # 可选，根据业务需求
):
    # 解码前端传来的URL
    decoded_url = unquote(url)
    """
    生成微信JS-SDK签名
    """
    # 1. 获取access_token
    token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WECHAT_CONFIG['appid']}&secret={WECHAT_CONFIG['secret']}"
    token_resp = requests.get(token_url)
    token_data = token_resp.json()

    if "access_token" not in token_data:
        logger.info(f"iOS_WX_Error: {token_data.get('errmsg', '未知错误')}")
        raise HTTPException(status_code=500, detail="获取access_token失败")

    access_token = token_data["access_token"]

    # 2. 获取jsapi_ticket
    ticket_url = f"https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={access_token}&type=jsapi"
    ticket_resp = requests.get(ticket_url)
    ticket_data = ticket_resp.json()

    if ticket_data.get("errcode") != 0:
        logger.info(f"iOS_WX_Ticket_Error: {ticket_data.get('errmsg', '未知错误')}")
        raise HTTPException(status_code=500, detail="获取jsapi_ticket失败")

    jsapi_ticket = ticket_data["ticket"]

    # 3. 生成签名
    noncestr = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    timestamp = str(int(time.time()))

    # 注意：URL必须与前端页面完全一致
    #signature_str = f"jsapi_ticket={jsapi_ticket}&noncestr={noncestr}&timestamp={timestamp}&url={decoded_url}"

    params = [
        f"jsapi_ticket={jsapi_ticket}",
        f"noncestr={noncestr}",
        f"timestamp={timestamp}",
        f"url={decoded_url}"  # 使用解码后的URL
    ]
    params.sort()  # 字典序排序
    signature_str = "&".join(params)

    # 计算签名
    signature = hashlib.sha1(signature_str.encode('utf-8')).hexdigest()
    logger.info(f"iOS_WX_Sign: url={url}, sig={signature}")

    return {
        "appId": WECHAT_CONFIG['appid'],
        "timestamp": timestamp,
        "nonceStr": noncestr,
        "signature": signature
    }




# 在FastAPI路由中添加以下接口
@app.post("/create-payment")
async def create_payment(
    request: dict = Body(...),
    openid: str = Depends(get_current_user)
):
    """
    创建微信JSAPI支付订单
    请求参数: {
        "amount": 20000,  # 金额(分)
        "description": "会员开通"
    }
    """
    # 1. 准备参数
    # amount = request.get('amount', 20000)  # 默认200元
    amount = 20000 # 默认200元
    description = request.get('description', '会员开通')

    # 2. 生成订单参数
    out_trade_no = f"PY{int(time.time())}{random.randint(1000, 9999)}"  # 商户订单号
    nonce_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    # 3. 构造统一下单参数
    params = {
        "appid": WECHAT_CONFIG['appid'],
        "mch_id": WECHAT_PAY_CONFIG['mch_id'],
        "nonce_str": nonce_str,
        "body": description[:128],  # 商品描述
        "out_trade_no": out_trade_no,
        "total_fee": amount,
        "spbill_create_ip": "127.0.0.1",  # 终端IP
        "notify_url": WECHAT_PAY_CONFIG['notify_url'],
        "trade_type": "JSAPI",
        "openid": openid
    }

    # 4. 生成签名
    sorted_params = sorted(params.items())
    sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
    sign_str += f"&key={WECHAT_PAY_CONFIG['api_key']}"
    sign = hashlib.md5(sign_str.encode()).hexdigest().upper()
    params['sign'] = sign

    # 5. 构造XML请求体
    xml_data = "<xml>"
    for k, v in params.items():
        xml_data += f"<{k}>{v}</{k}>"
    xml_data += "</xml>"

    # 6. 调用微信支付统一下单接口
    response = requests.post(
        "https://api.mch.weixin.qq.com/pay/unifiedorder",
        data=xml_data.encode('utf-8'),
        headers={'Content-Type': 'application/xml'}
    )

    logger.info(f"微信支付响应状态码: {response.status_code}")
    logger.info(f"微信支付响应内容: {response.text}")  # 打印原始XML
    # 7. 解析响应
    root = ET.fromstring(response.content)
    result = {child.tag: child.text for child in root}

    logger.info(f"微信支付返回结果: {result}")
    if result.get('return_code') != 'SUCCESS' or result.get('result_code') != 'SUCCESS':
        error_detail = f"""错误详情:
    return_code: {result.get('return_code')}
    return_msg: {result.get('return_msg')}
    err_code: {result.get('err_code')}
    err_code_des: {result.get('err_code_des')}
    """
        logger.info(error_detail)
        raise HTTPException(...)
        #raise HTTPException(
        #    status_code=400,
        #    detail=f"微信支付下单失败: {result.get('return_msg', result.get('err_code_des', '未知错误'))}"
        #)

    # 8. 生成JSAPI支付参数
    prepay_id = result['prepay_id']
    timestamp = str(int(time.time()))
    nonce_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    pay_params = {
        "appId": WECHAT_CONFIG['appid'],
        "timeStamp": timestamp,
        "nonceStr": nonce_str,
        "package": f"prepay_id={prepay_id}",
        "signType": "MD5"
    }

    # 9. 生成支付签名
    sorted_pay_params = sorted(pay_params.items())
    pay_sign_str = "&".join([f"{k}={v}" for k, v in sorted_pay_params])
    pay_sign_str += f"&key={WECHAT_PAY_CONFIG['api_key']}"
    pay_sign = hashlib.md5(pay_sign_str.encode()).hexdigest().upper()
    pay_params['paySign'] = pay_sign

    return pay_params

@app.post("/payment/notify")
async def payment_notify(request: Request):
    """
    微信支付结果回调接口
    """
    # 1. 解析XML数据
    body = await request.body()
    root = ET.fromstring(body)
    result = {child.tag: child.text for child in root}

    # 2. 验证签名
    sign = result.pop('sign', '')
    sorted_params = sorted(result.items())
    sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
    sign_str += f"&key={WECHAT_PAY_CONFIG['api_key']}"
    calculated_sign = hashlib.md5(sign_str.encode()).hexdigest().upper()

    if sign != calculated_sign:
        return Response(content="<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[签名失败]]></return_msg></xml>", media_type="application/xml")

    # 3. 处理支付结果
    if result['return_code'] == 'SUCCESS' and result['result_code'] == 'SUCCESS':
        # 支付成功，更新数据库
        openid = result['openid']
        out_trade_no = result['out_trade_no']
        transaction_id = result['transaction_id']
        total_fee = int(result['total_fee']) / 100  # 转换为元

        # TODO: 在这里更新数据库，记录支付成功状态

        try:
            with Session(engine) as session:
                with session.begin():
                    user = session.exec(select(User).where(User.openid == openid)).first()
                    if not user:
                        user = User(openid=openid)
                        session.add(user)
                        session.flush()

                    # 2. 计算有效期（1年后）
                    expire_at = datetime.now(beijing_tz) + timedelta(days=365)

                    # 3. 更新或插入 user_status 表
                    user_status = session.get(UserStatus, openid)
                    if user_status:
                        # 更新现有记录
                        user_status.expire_at = expire_at
                        user_status.state = 1  # 激活状态
                    else:
                        # 创建新记录
                        user_status = UserStatus(openid=openid, state=1, expire_at=expire_at)
                        session.add(user_status)
                    # 2.3 积分更新
                    session.add(UserPointsLog(user_id=user.id, action="recharge", points=int(total_fee)))
                    session.execute(
                        text("UPDATE user SET points = COALESCE(points, 0) + :p WHERE id = :uid"),
                        {"p": int(total_fee), "uid": user.id}
                    )

                    # 2.4 记录充值
                    session.add(UserRecharge(
                        openid=openid,
                        amount=total_fee,
                        transaction_id=transaction_id
                    ))

                    logger.info(f"支付成功: 订单号={out_trade_no}, 金额={total_fee}元")
                    logger.info(f"用户状态更新成功: openid={openid}, expire_at={expire_at}")

        except Exception as e:
            logger.error(f"数据库更新失败: {str(e)}")
            # 返回失败让微信重试
            return Response(content="<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[DB update failed]]></return_msg></xml>", media_type="application/xml")
        # 返回成功响应
        return Response(content="<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>", media_type="application/xml")

    # 支付失败
    return Response(content="<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[支付失败]]></return_msg></xml>", media_type="application/xml")

# 创建日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # 获取客户端IP
    client_ip = request.client.host if request.client else "unknown"

    # 尝试获取openid（但不影响性能）
    openid = "anonymous"
    try:
        # 从头部获取Authorization
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_jwt_token(token)
            openid = payload.get("sub", "anonymous")
    except Exception:
        pass  # 忽略所有错误，不影响主要流程

    # 调用下一个中间件/路由
    response = await call_next(request)

    # 计算处理时间
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)

    # 记录日志
    logger.info(
        f"IP: {client_ip} - "
        f"OpenID: {openid} - "
        f"Method: {request.method} - "
        f"Path: {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {formatted_process_time}ms"
    )

    return response


# 添加支付状态检查接口
@app.get("/check-payment")
async def check_payment_status(
    openid: str = Depends(get_current_user)
):
    """
    检查用户支付状态
    返回: {
        "is_paid": bool,
        "expire_at": str (ISO格式) | null
    }
    """
    with Session(engine) as session:
        try:
            # 获取用户ID
            # user = session.exec(select(User.id).where(User.openid == openid)).first()
            # print('看看user:', user)
            # if not user:
            #     raise HTTPException(status_code=404, detail="用户不存在")

            # # 查询支付状态表
            # stmt = text("""
            #     SELECT state, expire_at
            #     FROM user_status
            #     WHERE id = :user_id
            # """)
            # result = session.execute(stmt, {"user_id": user}).first()
            stmt = select(UserStatus).where(UserStatus.openid == openid)
            user_status = session.exec(stmt).first()
            if not user_status:
                return {"is_paid": False, "expire_at": None}

            expire_at = user_status.expire_at
            now = datetime.now(beijing_tz)
            print('expire_at:',expire_at)
            if expire_at:
                # 假设数据库存储的是UTC时间
                # expire_at = expire_at.replace(tzinfo=timezone.utc)

                # 或者假设数据库存储的是北京时间
                # expire_at = expire_at.replace(tzinfo=beijing_tz)
                if isinstance(expire_at, datetime):
                    # 如果数据库存储的是UTC时间且没有时区信息
                    if expire_at.tzinfo is None:
                        expire_at = expire_at.replace(tzinfo=timezone.utc)
                    # 转换为北京时间
                    expire_at = expire_at.astimezone(beijing_tz)
                else:
                    # 处理非datetime对象的情况
                    logger.warning(f"expire_at不是datetime对象: {type(expire_at)}")
                    expire_at = None
            # 检查状态和有效期
            is_active =  expire_at and expire_at > now

            return {
                "is_paid": is_active,
                "expire_at": expire_at.isoformat() if expire_at else None
            }
        except Exception as e:
            logger.error(f"支付状态查询失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="支付状态查询失败:"
            )

@app.get("/newcomers")
@cache(expire=300)  # Cache for 1 minute to reduce database load
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
            logger.error(f"获取新用户失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="获取新用户失败"
            )

# 新增照片上传接口
@app.post("/upload-photo")
@limiter.limit("10/minute")
async def upload_photo(
    request: Request,
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
        logger.error(f"文件保存失败: {str(e)}")
        raise HTTPException(status_code=500, detail="文件保存失败")

    if not validate_file_magic(file_path):
        os.remove(file_path)
        raise HTTPException(400, "文件内容不合法")
    # 异步压缩图片
    # try:
    #     loop = asyncio.get_event_loop()
    #     await loop.run_in_executor(None, compress_image, file_path)
    # except Exception as e:
    #     logger.info(f"图片压缩失败: {str(e)}")
    try:
        # 同步压缩图片（添加超时处理）
        loop = asyncio.get_event_loop()
        compression_success = await loop.run_in_executor(
            None,
            lambda: compress_image(file_path, timeout=3)  # 3秒超时
        )

        if not compression_success:
            logger.warning(f"Photo compression failed: {file_path}")
            # 压缩失败时删除文件（可能是恶意文件）
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail="图片处理失败，请上传有效的图片文件"
            )
    except asyncio.TimeoutError:
        logger.error(f"Photo compression timed out: {file_path}")
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail="图片处理超时，文件可能过大或格式复杂"
        )

    return {"filename": unique_filename}

# 新增照片删除接口
class DeletePhotoRequest(BaseModel):
    photo_name: str

@app.post("/delete-photo")
async def delete_photo(
    request: DeletePhotoRequest,
    openid: str = Depends(get_current_user)
):
    logger.info(f"Deleting photo: {request.photo_name} for user: {openid}")

    # 安全检查
    if not request.photo_name or any(c in request.photo_name for c in ['/', '\\', '..']):
        raise HTTPException(status_code=400, detail="无效的文件名")

    file_path = os.path.join(UPLOAD_PHOTO_DIR, request.photo_name)

    # 检查文件是否存在（但即使不存在也继续数据库操作）
    file_exists = os.path.exists(file_path)

    # 数据库操作
    with Session(engine) as session:
        # 开启事务
        with session.begin():
            user = session.exec(select(User).where(User.openid == openid)).first()
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")

            # 更新user表的照片列表
            photos = [p for p in user.photo.split(',') if p] if user.photo else []
            if request.photo_name in photos:
                photos.remove(request.photo_name)
                user.photo = ','.join(photos)
                session.add(user)

            # 更新user_tmp表的照片列表
            user_tmp = session.exec(select(UserTmp).where(UserTmp.openid == openid)).first()
            if user_tmp:
                tmp_photos = [p for p in user_tmp.photo.split(',') if p] if user_tmp.photo else []
                if request.photo_name in tmp_photos:
                    tmp_photos.remove(request.photo_name)
                    user_tmp.photo = ','.join(tmp_photos)
                    session.add(user_tmp)

    # 删除文件（在事务外执行）
    if file_exists:
        try:
            os.remove(file_path)
            logger.info(f"照片删除成功: {request.photo_name}")
            return {"status": "success", "message": "照片删除成功"}
        except Exception as e:
            logger.error(f"文件删除失败: {str(e)}")
            # 即使文件删除失败，数据库操作已成功，返回部分成功状态
            return {
                "status": "partial_success",
                "message": "数据库更新成功，但文件删除失败",
                "details": str(e)
            }
    else:
        logger.warning(f"照片文件不存在: {request.photo_name}")
        return {
            "status": "partial_success",
            "message": "数据库更新成功，但照片文件不存在"
        }

# 新增保存照片列表接口
@app.post("/save-photos")
async def save_photos(
    photos_data: dict,
    openid: str = Depends(get_current_user)
):
    photos_list = photos_data.get("photos", [])
    photos_str = ','.join(photos_list)
    old_photos = []  # 用于记录旧照片列表

    with Session(engine) as session:
        # 开启事务
        with session.begin():
            # 更新user表
            user = session.exec(select(User).where(User.openid == openid)).first()
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")

            # 保存旧照片列表以便后续清理
            old_photos = user.photo.split(',') if user.photo else []

            # 更新user表照片
            user.photo = photos_str
            user.first_photo = photos_list[0] if photos_list else None
            session.add(user)

            # 更新user_tmp表
            user_tmp = session.exec(select(UserTmp).where(UserTmp.openid == openid)).first()
            if user_tmp:
                user_tmp.photo = photos_str
                session.add(user_tmp)

    # 在事务外清理旧照片（避免影响事务性能）
    for old_photo in old_photos:
        if old_photo and old_photo not in photos_list:
            old_path = os.path.join(UPLOAD_PHOTO_DIR, old_photo)
            try:
                if os.path.exists(old_path):
                    os.remove(old_path)
                    logger.info(f"已删除旧照片: {old_photo}")
            except Exception as e:
                logger.error(f"无法删除旧照片 {old_photo}: {str(e)}")

    return {"status": "success", "message": "照片列表保存成功"}

# 图片压缩函数
# 图片压缩函数（添加安全检查和超时处理）
def compress_image(file_path, max_size=800, timeout=5):
    start_time = time.time()

    try:
        # 1. 使用 Pillow 验证图片类型
        try:
            with Image.open(file_path) as img:
                # 获取图片格式
                image_format = img.format
                if image_format not in ['JPEG', 'PNG', 'GIF', 'BMP']:
                    logger.error(f"Unsupported image format: {image_format} for file {file_path}")
                    return False

                # 验证图片完整性
                img.verify()
        except (UnidentifiedImageError, OSError, SyntaxError) as e:
            logger.error(f"Invalid image: {file_path} - {str(e)}")
            return False

        # 2. 重新打开图片进行压缩
        with Image.open(file_path) as img:
            # 3. 检查处理时间
            if time.time() - start_time > timeout:
                logger.warning(f"Image processing timeout: {file_path}")
                return False

            # 4. 设置最大尺寸
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)

            # 5. 设置质量参数
            quality = 80

            # 6. 如果是PNG且尺寸较大，转换为JPG
            if image_format == 'PNG' and max(img.size) > 500:
                output_path = os.path.splitext(file_path)[0] + '.jpg'
                img = img.convert('RGB')
                img.save(output_path, 'JPEG', quality=quality)
                os.remove(file_path)  # 删除原PNG文件
                return output_path

            # 7. 保存压缩后的图片
            img.save(file_path, quality=quality)
            return file_path

    except Exception as e:
        logger.error(f"Image compression failed: {file_path} - {str(e)}")
        return False

def compress_image_bak(file_path):
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
        logger.info(f"图片压缩失败: {str(e)}")
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

#
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
        # 1. 获取当前用户ID
        stmt = select(User.id).where(User.openid == openid)
        current_user = session.exec(stmt).first()
        if not current_user:
            raise HTTPException(status_code=404, detail="用户不存在")

        current_user_id = current_user

        # 2. 查询我喜欢的（过滤状态）
        ilike_stmt = text("""
            SELECT ul.liked_id AS user_id, ul.created_at
            FROM user_likes ul
            JOIN user u ON u.id = ul.liked_id
            JOIN user_status us ON us.openid = u.openid
            WHERE ul.liker_id = :current_user_id
              AND us.state = 1
              AND (us.expire_at IS NULL OR us.expire_at > NOW())
        """)
        ilike_results = session.execute(ilike_stmt, {"current_user_id": current_user_id}).mappings().all()

        # 3. 查询喜欢我的（过滤状态）
        likeme_stmt = text("""
            SELECT ul.liker_id AS user_id, ul.created_at
            FROM user_likes ul
            JOIN user u ON u.id = ul.liker_id
            JOIN user_status us ON us.openid = u.openid
            WHERE ul.liked_id = :current_user_id
              AND us.state = 1
              AND (us.expire_at IS NULL OR us.expire_at > NOW())
        """)
        likeme_results = session.execute(likeme_stmt, {"current_user_id": current_user_id}).mappings().all()

        # 4. 格式化结果
        ilike = [{
            "user_id": row["user_id"],
            "created_at": row["created_at"].isoformat()
        } for row in ilike_results]

        likeme = [{
            "user_id": row["user_id"],
            "created_at": row["created_at"].isoformat()
        } for row in likeme_results]

        return {
            "ilike": ilike,
            "likeme": likeme
        }

# @app.get("/get-likes")
# async def get_likes(
#     openid: str = Depends(get_current_user)
# ):
#     with Session(engine) as session:
#         # 1. 根据openid获取当前用户ID
#         stmt = select(User.id).where(User.openid == openid)
#         current_user = session.exec(stmt).first()

#         if not current_user:
#             raise HTTPException(status_code=404, detail="用户不存在")

#         current_user_id = current_user

#         # 2. 分别查询 ilike 和 likeme
#         # 查询 ilike (我喜欢的)
#         ilike_stmt = select(
#             UserLike.liked_id.label("user_id"),
#             UserLike.created_at
#         ).where(UserLike.liker_id == current_user_id)

#         ilike_results = session.exec(ilike_stmt).all()

#         # 查询 likeme (喜欢我的)
#         likeme_stmt = select(
#             UserLike.liker_id.label("user_id"),
#             UserLike.created_at
#         ).where(UserLike.liked_id == current_user_id)

#         likeme_results = session.exec(likeme_stmt).all()

#         # 3. 处理结果
#         ilike = [{
#             "user_id": row.user_id,
#             "created_at": row.created_at.isoformat()
#         } for row in ilike_results]

#         likeme = [{
#             "user_id": row.user_id,
#             "created_at": row.created_at.isoformat()
#         } for row in likeme_results]

#         return {
#             "ilike": ilike,
#             "likeme": likeme
#         }

# 异步记录访问的函数
async def record_visit(target_id: int, visitor_id: int):
    try:
        with Session(engine) as session:
            # 使用原生SQL提高性能
            session.execute(
                text("""
                    INSERT INTO cj.user_visits (target_id, visitor_id)
                    VALUES (:target_id, :visitor_id)
                """),
                {"target_id": target_id, "visitor_id": visitor_id}
            )
            session.commit()
    except Exception as e:
        logger.info(f"访问记录插入失败: {str(e)}")

@app.get("/getpendingaudit")
async def get_pending_audit_count(
    openid: str = Depends(get_current_user)
):
    """
    获取待审核的用户资料数量
    """
    try:
        with Session(engine) as session:
            statement = select(func.count()).where(
                UserTmp.state == 0,
                UserTmp.gender.is_not(None)
            )
            count = session.exec(statement).one()
            return {"count": count}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取待审核数量失败: {str(e)}"
        )

# 新增保存资料接口
@app.post("/profile")
async def add_profile(
    profile_data: ProfileData,
    openid: str = Depends(get_current_user)
):
    # 获取当前时间
    current_time = datetime.now(timezone.utc)

    with Session(engine) as session:
        # 检查user_tmp表中是否已有该openid的记录
        user_tmp = session.exec(
            select(UserTmp)
            .where(UserTmp.openid == openid)
        ).first()

        if user_tmp:
            # 更新现有记录
            for key, value in profile_data.model_dump().items():
                setattr(user_tmp, key, value)
            user_tmp.state = 0  # 重置为待审核状态
            user_tmp.updated_at = current_time
        else:
            # 创建新记录
            user_tmp = UserTmp(
                openid=openid,
                id=str(uuid4()),
                **profile_data.model_dump(),
                state=0,  # 待审核状态
                created_at=current_time,
                updated_at=current_time
            )
            session.add(user_tmp)

        session.commit()

    return {"status": "success", "message": "资料已提交审核"}


@app.get("/getlasttime")
async def get_last_time():
    """
    返回：max(
        max(user.updated_at),
        max(user_status.last_mod_date),
        max(expire_at 且 expire_at < NOW())
    )
    """
    with Session(engine) as session:
        now = datetime.now(beijing_tz)

        # 1. 最大的 user.updated_at
        max_user = session.scalar(
            text("SELECT MAX(updated_at) FROM user")
        )

        # 2. 最大的 user_status.last_mod_date
        max_status = session.scalar(
            text("SELECT MAX(last_mod_date) FROM user_status")
        )

        # 3. 已过期用户中最大的 expire_at（且 < NOW）
        max_expired = session.scalar(
            text("""
                SELECT MAX(expire_at)
                FROM user_status
                WHERE expire_at IS NOT NULL
                  AND expire_at < :now
            """),
            {"now": now}
        )

        # 合并并取最大
        times = [t for t in (max_user, max_status, max_expired) if t]
        latest = max(times) if times else None

        return {"lasttime": latest.isoformat() if latest else None}
# @app.get("/getlasttime")
# async def get_last_time():
#     """
#     获取cj.user表中最大的updated_at时间戳
#     返回格式: { "lasttime": "2023-01-01T00:00:00" } 或 { "lasttime": null }
#     """
#     with Session(engine) as session:
#         try:
#             # 高效查询 (使用数据库索引)
#             stmt = select(func.max(User.updated_at).label("max_time"))
#             result = session.execute(stmt).scalar_one_or_none()

#             return {
#                 "lasttime": result.isoformat() if result else None
#             }

#         except Exception as e:
#             logger.error(f"查询最新时间失败: {str(e)}")
#             raise HTTPException(
#                 status_code=500,
#                 detail="查询最新时间失败"
#             )

def validate_file_magic(file_path: str) -> bool:
    """使用魔数验证文件真实类型"""
    try:
        mime = magic.from_file(file_path, mime=True)
        return mime.startswith('image/')
    except Exception:
        return False

@app.post("/upload-avatar")
@limiter.limit("5/minute")
async def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    openid: str = Depends(get_current_user)
):
    # 验证文件类型
    content_type = file.content_type
    if not content_type or not content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只能上传图片文件")

    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1].lower()
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
                    os.remove(file_path)
                    raise HTTPException(status_code=400, detail="图片大小不能超过5MB")
                f.write(chunk)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"文件保存失败: {str(e)}")
        raise HTTPException(status_code=500, detail="文件保存失败")

    if not validate_file_magic(file_path):
        os.remove(file_path)
        raise HTTPException(400, "文件内容不合法")

    # 图片压缩处理
    try:
        loop = asyncio.get_event_loop()
        compression_success = await loop.run_in_executor(
            None,
            lambda: compress_image(file_path, timeout=3)
        )

        if not compression_success:
            logger.warning(f"Avatar compression failed: {file_path}")
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail="图片处理失败，请上传有效的图片文件"
            )
    except asyncio.TimeoutError:
        logger.error(f"Avatar compression timed out: {file_path}")
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail="图片处理超时，文件可能过大或格式复杂"
        )

    old_avatar_user = None  # 用于记录user表的旧头像

    try:
        with Session(engine) as session:
            # 开启事务
            with session.begin():
                # 1. 更新或创建user_tmp记录
                user_tmp = session.exec(select(UserTmp).where(UserTmp.openid == openid)).first()
                if user_tmp:
                    # 更新user_tmp表
                    user_tmp.avatar = unique_filename
                else:
                    # 如果不存在则创建新记录
                    user_tmp = UserTmp(openid=openid, avatar=unique_filename)
                    session.add(user_tmp)

                # 2. 如果user表存在则更新，并记录旧头像
                user = session.exec(select(User).where(User.openid == openid)).first()
                if user:
                    old_avatar_user = user.avatar  # 记录user表的旧头像
                    user.avatar = unique_filename  # 更新user表

                # 提交事务
                session.commit()
    except Exception as e:
        # 回滚事务并删除新上传的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"数据库更新失败: {str(e)}")
        raise HTTPException(status_code=500, detail="数据库更新失败")

    # 只删除user表中的旧头像（如果存在）
    if old_avatar_user:
        old_path = os.path.join(UPLOAD_DIR, old_avatar_user)
        try:
            if os.path.exists(old_path) and os.path.isfile(old_path):
                os.remove(old_path)
        except Exception as e:
            logger.info(f"警告: 无法删除旧头像 {old_avatar_user}: {str(e)}")

    # 返回头像URL
    avatar_url = f"/avatars/{unique_filename}"
    return {"avatar_url": avatar_url}

@app.post("/upload-avatar-bak")
@limiter.limit("5/minute")
async def upload_avatar_bak(
    request: Request,
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
        logger.error(f"文件保存失败: {str(e)}")
        raise HTTPException(status_code=500, detail="文件保存失败")

    if not validate_file_magic(file_path):
        os.remove(file_path)
        raise HTTPException(400, "文件内容不合法")
    # 保存文件后添加压缩
    try:
        # 同步压缩图片（添加超时处理）
        loop = asyncio.get_event_loop()
        compression_success = await loop.run_in_executor(
            None,
            lambda: compress_image(file_path, timeout=3)  # 3秒超时
        )

        if not compression_success:
            logger.warning(f"Avatar compression failed: {file_path}")
            # 压缩失败时删除文件（可能是恶意文件）
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail="图片处理失败，请上传有效的图片文件"
            )
    except asyncio.TimeoutError:
        logger.error(f"Avatar compression timed out: {file_path}")
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail="图片处理超时，文件可能过大或格式复杂"
        )
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
        logger.error(f"数据库更新失败: {str(e)}")
        raise HTTPException(status_code=500, detail="数据库更新失败")

    # 成功更新后删除旧头像
    if old_avatar:
        old_path = os.path.join(UPLOAD_DIR, old_avatar)
        # logger.info(f"尝试删除旧头像: {old_path}")
        try:
            if os.path.exists(old_path) and os.path.isfile(old_path):
                os.remove(old_path)
        except Exception as e:
            # 删除失败不影响主要操作，但应记录日志
            logger.info(f"警告: 无法删除旧头像 {old_avatar}: {str(e)}")

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
        # 开启事务
        with session.begin():
            # 更新user表
            user = session.exec(select(User).where(User.openid == openid)).first()
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            user.nickname = nickname

            # 更新user_tmp表
            user_tmp = session.exec(select(UserTmp).where(UserTmp.openid == openid)).first()
            if user_tmp:
                user_tmp.nickname = nickname
                session.add(user_tmp)

            session.add(user)

    return {"status": "success", "message": "昵称更新成功"}

@app.get("/check/user_first")
async def check_user_tmp_exists(current_user_openid: str = Depends(get_current_user)):
    """
    根据根据当前登录用户的token获取openid，查询user_tmp表中是否存在该用户记录
    返回值：存在返回{"result": 1}，不存在返回{"result": 0}
    """
    with Session(engine) as session:
        # 查询user_tmp表中是否存在该openid的记录
        user_tmp = session.exec(
            select(UserTmp).where(UserTmp.openid == current_user_openid)
        ).first()
        # 存在返回1，不存在返回0
        return {"result": 1 if user_tmp else 0}

@app.get("/getprofile")
async def get_profile(openid: str = Depends(get_current_user)):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.openid == openid)).first()
        #print('user:',user)
        if not user:

            raise HTTPException(404, "用户资料未找到")

        # ---------- 每日登录积分 ----------
        # today = datetime.now(beijing_tz).date()
        #print('user:',user.id)
        already = session.exec(
            select(UserPointsLog)
            .where(
                UserPointsLog.user_id == user.id,
                UserPointsLog.action == "login",
                func.date(UserPointsLog.created_at) == func.curdate()
            )
        ).first()

        #print('already:',already)
        if not already:
            session.add(UserPointsLog(user_id=user.id, action="login", points=2))
            session.execute(
                text("UPDATE user SET points = COALESCE(points, 0) + 2 WHERE id = :uid"),
                {"uid": user.id}
            )
            session.commit()
        # ---------------------------------

        return user.model_dump(exclude={"openid"})

# 新增管理功能所需的模型
class UserStatus(SQLModel, table=True):
    __tablename__ = "user_status"
    id: int
    openid: str = Field(primary_key=True)
    state: int = Field(default=1)  # 0:禁用, 1:正常
    expire_at: Optional[datetime] = Field(default=None)

class UserTop(SQLModel, table=True):
    __tablename__ = "user_top"
    id: int = Field(primary_key=True, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(beijing_tz))

class SystemSlogan(SQLModel, table=True):
    __tablename__ = "system_slogans"
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(max_length=255)
    created_by: Optional[str] = Field(max_length=128)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP")
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default="CURRENT_TIMESTAMP",
            onupdate="CURRENT_TIMESTAMP"
        )
    )

# 用户管理响应模型
class AdminUserResponse(BaseModel):
    id: int
    nickname: Optional[str]
    gender: Optional[str]
    avatar: Optional[str]
    points: Optional[int]
    like_count: Optional[int]
    is_top: Optional[bool]
    state: Optional[int]
    expire_at: Optional[datetime]

# 更新用户状态请求模型
class UpdateUserStatusRequest(BaseModel):
    is_active: bool

# 管理员工具函数
def is_admin(openid: str) -> bool:
    ADMIN_LIST = ["oagEzvoOkgU-P6ynIDKw8MoTR91w"]
    # oagEzvoOkgU-P6ynIDKw8MoTR91w
    # oagEzvlgS2fE90_gROtw9XcH0ELU
    return openid in ADMIN_LIST
    # return True

# 管理员依赖项
async def get_admin_user(authorization: str = Header(...)) -> str:
    openid = await get_current_user(authorization)
    if not is_admin(openid):
        raise HTTPException(status_code=403, detail="无管理权限")
    return openid

@app.get("/admin/users", response_model=list[AdminUserResponse])
async def get_users_with_likes(
    openid: str = Depends(get_admin_user),
    gender: Optional[str] = None,
    is_top: Optional[bool] = None,
    keyword: Optional[str] = None,
    points: Optional[int] = None,
    page: int = 1,
    pageSize: int = 20
):
    # 计算偏移量
    offset = (page - 1) * pageSize

    with Session(engine) as session:
        # 构建基础SQL查询
        base_sql = """
        SELECT
            u.id,
            u.nickname,
            u.gender,
            u.avatar,
            u.points,
            COUNT(ul.liked_id) AS like_count,
            us.state as state,
            ut.id IS NOT NULL AS is_top,
            us.expire_at as expire_at
        FROM
            user u
        LEFT JOIN
            user_likes ul ON u.id = ul.liked_id
        LEFT JOIN
            user_status us ON u.id = us.id
        LEFT JOIN
            user_top ut ON u.id = ut.id
        """

        # 构建WHERE条件
        conditions = []
        params = {}

        if gender:
            conditions.append("u.gender = :gender")
            params["gender"] = gender

        if is_top is not None:
            if is_top:
                conditions.append("ut.id IS NOT NULL")
            else:
                conditions.append("ut.id IS NULL")

        if keyword:
            conditions.append("(u.nickname LIKE :keyword OR u.id LIKE :keyword)")
            params["keyword"] = f"%{keyword}%"

        # 组合WHERE子句
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        # 构建完整SQL
        sql = f"""
        {base_sql}
        {where_clause}
        GROUP BY
            u.id, u.nickname, u.gender, u.avatar, us.state, ut.id, us.expire_at, u.points
        ORDER BY
            is_top DESC,
            like_count DESC
        LIMIT :limit OFFSET :offset
        """

        # 添加分页参数
        params["limit"] = pageSize
        params["offset"] = offset

        # 执行查询
        result = session.execute(text(sql), params)
        rows = result.mappings().all()

        # 处理结果
        return rows

ADMIN_MENU_ITEM = {
    "id": "manacenter",
    "label": "管理",
    "iconType": "mana",  # 前端映射的图标类型
    "iconSelected": "manaSelectedIcon",
    "to": "/manacenter",
    "requiredPermission": "admin:access"
}

@app.get("/menu")
async def get_user_menu(openid: str = Depends(get_current_user)):
    """
    获取用户菜单
    只有管理员会返回管理菜单项
    """
    print('openid: ',openid)
    if is_admin(openid):
        return {
            "menuItems": [ADMIN_MENU_ITEM],
            "permissions": ["admin:access"]  # 同时返回权限列表
        }
    return {
        "menuItems": [],
        "permissions": []
    }

# 修改置顶/取消置顶接口
@app.post("/admin/users/{user_id}/toggle-top")
async def toggle_user_top(
    user_id: int,
    request: dict,
    openid: str = Depends(get_admin_user)
):
    """
    管理员置顶 / 取消置顶用户
    1. 操作 user_top 表（插入 / 删除）
    2. 同步 user 表和 user_tmp 表的 istop 字段
    事务保证一致性
    """
    is_top = bool(request.get("is_top"))

    with Session(engine) as session:
        with session.begin():  # 事务开始
            # 1. 确保目标用户在 user 表中存在
            user = session.get(User, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")

            # 2. 操作 user_top 表
            existing_top = session.exec(
                select(UserTop).where(UserTop.id == user_id)
            ).first()

            if is_top:
                if existing_top:
                    return {"status": "success", "message": "用户已置顶"}
                session.add(UserTop(id=user_id))
            else:
                if not existing_top:
                    raise HTTPException(status_code=404, detail="该用户未置顶")
                session.delete(existing_top)

            # 3. 更新 user 表的 istop
            user.istop = 1 if is_top else 0

            # 4. 更新 user_tmp 表的 istop（如果存在）
            user_tmp = session.exec(
                select(UserTmp).where(UserTmp.openid == user.openid)
            ).first()
            if user_tmp:
                user_tmp.istop = 1 if is_top else 0

        # 事务自动提交

    return {
        "status": "success",
        "message": "置顶成功" if is_top else "取消置顶成功"
    }
# @app.post("/admin/users/{user_id}/toggle-top")
# async def toggle_user_top(
#     user_id: int,
#     request: dict,  # 改为接收字典对象
#     openid: str = Depends(get_admin_user)
# ):
#     is_top = request.get("is_top", False)  # 从请求体中获取 is_top 值
#     with Session(engine) as session:
#         if is_top:
#             # 检查是否已经置顶
#             existing_top = session.exec(
#                 select(UserTop).where(UserTop.id == user_id)
#             ).first()
#             if existing_top:
#                 return {"status": "success", "message": "用户已置顶"}

#             new_top = UserTop(id=user_id)
#             session.add(new_top)
#             session.commit()
#             return {"status": "success", "message": "置顶成功"}
#         else:
#             # 取消置顶
#             result = session.exec(
#                 delete(UserTop).where(UserTop.id == user_id)
#             )
#             session.commit()
#             if result.rowcount == 0:
#                 raise HTTPException(status_code=404, detail="该用户未置顶")
#             return {"status": "success", "message": "取消置顶成功"}

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

@app.get("/user-mana/{user_id}")
async def get_user_for_admin(
    user_id: int,
    openid: str = Depends(get_admin_user)  # 使用管理员依赖项
):
    """
    管理员获取用户详情接口
    返回完整的用户信息（排除openid），不包含点赞状态
    """
    with Session(engine) as session:
        try:
            # 查询目标用户信息
            target_user = session.exec(
                select(User).where(User.id == user_id)
            ).first()

            if not target_user:
                raise HTTPException(status_code=404, detail="目标用户未找到")

            # 直接返回用户数据，排除openid字段
            return target_user.model_dump(exclude={"openid"})

        except Exception as e:
            logger.info(f"管理员获取用户详情出错: {str(e)}")
            raise HTTPException(status_code=500, detail="服务器内部错误")




def setup_background_cleaner():
    """设置后台清理任务（备选方案）"""
    from apscheduler.schedulers.background import BackgroundScheduler

    def clean_old_visits():
        with Session(engine) as session:
            try:
                one_month_ago = datetime.now() - timedelta(days=30)
                session.execute(
                    text("DELETE FROM user_visits WHERE created_at < :cutoff"),
                    {"cutoff": one_month_ago}
                )
                session.commit()
            except Exception as e:
                logger.info(f"自动清理失败: {str(e)}")

    scheduler = BackgroundScheduler()
    scheduler.add_job(clean_old_visits, 'interval', hours=1)
    scheduler.start()

@app.get("/explore_people_dic")
@cache(expire=300)
async def explore_people_dic():
    with Session(engine) as session:
        try:
            # 获取最大更新时间
            lasttime_stmt = text("""
                SELECT MAX(u.updated_at) as lasttime
                FROM user u
                LEFT JOIN user_status us ON u.openid = us.openid
                WHERE us.state = 1 AND us.expire_at > NOW()
            """)
            lasttime_result = session.execute(lasttime_stmt).fetchone()
            lasttime = lasttime_result[0] if lasttime_result else None

            # 查询用户数据（含过滤条件）
            users_stmt = text("""
                SELECT
                    u.id,
                    u.gender,
                    u.birth_date,
                    u.height,
                    u.avatar,
                    u.education,
                    u.income_level,
                    u.mem,
                    u.nickname,
                    u.occupation,
                    u.first_photo as photo,
                    u.region_code,
                    u.weight,
                    u.tip,
                    u.istop,
                    u.married,
                    u.child,
                    u.points,
                    us.expire_at
                FROM user u
                LEFT JOIN user_status us ON u.openid = us.openid
                WHERE us.state = 1 AND us.expire_at > NOW()
            """)

            users = session.execute(users_stmt).fetchall()

            # 构建返回字典
            people_dict = OrderedDict()
            for user in users:
                birth_date = user.birth_date.strftime('%Y-%m-%dT%H:%M:%S') if user.birth_date else None
                expire_at = user.expire_at.isoformat() if user.expire_at else None

                people_dict[str(user.id)] = {
                    'id': user.id,
                    'gender': user.gender,
                    'birth_date': birth_date,
                    'height': user.height,
                    'avatar': user.avatar,
                    'education': user.education,
                    'income_level': user.income_level,
                    'mem': user.mem,
                    'nickname': user.nickname,
                    'occupation': user.occupation,
                    'photo': user.photo,
                    'region_code': user.region_code,
                    'weight': user.weight,
                    'tip': float(user.tip) if user.tip else 0.0,
                    'istop': user.istop or 0,
                    'married': user.married or 0,
                    'child': user.child or 0,
                    'points': user.points or 0,
                    'expire_at': expire_at
                }

            return {
                "people": people_dict,
                "lasttime": lasttime.isoformat() if lasttime else None
            }

        except Exception as e:
            logger.error(f"explore_people_dic 查询失败: {str(e)}")
            return {
                "people": {},
                "lasttime": None
            }

@app.get("/explore_people_dic_old")
@cache(expire=300)
async def explore_people_dic_old():
    with Session(engine) as session:
        try:
            # 第一次查询：获取最大更新时间
            lasttime_stmt = text("SELECT MAX(updated_at) as lasttime FROM user")
            lasttime_result = session.execute(lasttime_stmt).fetchone()
            lasttime = lasttime_result[0] if lasttime_result else None

            # 第二次查询：获取所有用户数据
            users_stmt = text("""
                SELECT
                    id, gender, birth_date, height, avatar, education,
                    income_level, mem, nickname, occupation, first_photo as photo,
                    region_code, weight, tip, istop, married, child, points
                FROM user
            """)
            users = session.execute(users_stmt).fetchall()

            # 构建用户字典，键为字符串形式的用户ID
            people_dict = OrderedDict()
            for user in users:
                # 格式化出生日期（如果存在）
                birth_date = user.birth_date.strftime('%Y-%m-%dT%H:%M:%S') if user.birth_date else None

                people_dict[str(user.id)] = {
                    'id': user.id,
                    'gender': user.gender,
                    'birth_date': birth_date,
                    'height': user.height,
                    'avatar': user.avatar,
                    'education': user.education,
                    'income_level': user.income_level,
                    'mem': user.mem,
                    'nickname': user.nickname,
                    'occupation': user.occupation,
                    'photo': user.photo,
                    'region_code': user.region_code,
                    'weight': user.weight,
                    'tip': float(user.tip) if user.tip else 0.0,
                    'istop': user.istop or 0,
                    'married': user.married or 0,
                    'child': user.child or 0,
                    'points': user.points or 0,
                }

            return {
                "people": people_dict,  # 直接返回字典对象
                "lasttime": lasttime.isoformat() if lasttime else None
            }

        except Exception as e:
            logger.info(f"Database error: {str(e)}")
            return {
                "people": {},
                "lasttime": None
            }

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
            logger.info(f"Database error: {str(e)}")
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
class SinceBody(BaseModel):
    since: str  # ISO 字符串
@app.post('/explore_people_updated_dic')
async def explore_people_updated_dic(request_body: SinceBody):
    from datetime import datetime

    beijing_tz = timezone(timedelta(hours=8))
    try:
        since_dt = datetime.fromisoformat(request_body.since)
        # since_dt = datetime.fromisoformat(since.replace('Z', '+00:00')).astimezone(beijing_tz)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid since parameter")
    now = datetime.now(beijing_tz)

    with Session(engine) as session:
        # 1️⃣ 资料正常更新
        updated_users_stmt = text("""
            SELECT u.*
            FROM user u
            JOIN user_status us ON us.openid = u.openid
            WHERE u.updated_at > :since
              AND us.state = 1
              AND (us.expire_at IS NULL OR us.expire_at > :now)
        """)
        updated_users = session.execute(updated_users_stmt, {"since": since_dt, "now": now}).mappings().all()

        # 2️⃣ 最近被启用（state=1 且 last_mod_date > since）
        enabled_users_stmt = text("""
            SELECT u.*
            FROM user u
            JOIN user_status us ON us.openid = u.openid
            WHERE us.state = 1
              AND us.last_mod_date > :since
              AND (us.expire_at IS NULL OR us.expire_at > :now)
        """)
        enabled_users = session.execute(enabled_users_stmt, {"since": since_dt, "now": now}).mappings().all()

        # 3️⃣ 最近过期
        expired_ids_stmt = text("""
            SELECT u.id AS id
            FROM user u
            JOIN user_status us ON us.openid = u.openid
            WHERE us.expire_at > :since
            AND us.expire_at <= :now
        """)
        expired_ids = [r["id"] for r in session.execute(expired_ids_stmt, {"since": since_dt, "now": now}).mappings().all()]

        # 4️⃣ 最近被禁用
        disabled_ids_stmt = text("""
            SELECT u.id AS id
            FROM user u
            JOIN user_status us ON us.openid = u.openid
            WHERE us.state = 0
            AND us.last_mod_date > :since
        """)
        disabled_ids = [r["id"] for r in session.execute(disabled_ids_stmt, {"since": since_dt}).mappings().all()]

        # 合并需移除的ID（去重）
        removed_ids = list(set(expired_ids + disabled_ids))

        # 合并更新+启用用户（去重）
        all_valid = {u["id"]: u for u in updated_users + enabled_users}

        updates = {}
        for uid, user in all_valid.items():
            if uid in removed_ids:
                continue  # 如果同时出现在 removed 中，优先级：移除 > 启用
            updates[str(uid)] = {
                "id": user["id"],
                "nickname": user["nickname"],
                "gender": user["gender"],
                "birth_date": user["birth_date"].isoformat() if user["birth_date"] else None,
                "height": user["height"],
                "weight": user["weight"],
                "region_code": user["region_code"],
                "occupation": user["occupation"],
                "education": user["education"],
                "income_level": user["income_level"],
                "mem": user["mem"],
                "avatar": user["avatar"],
                "photo": user["photo"],
                "tip": float(user["tip"]) if user["tip"] else 0.0,
                "istop": user["istop"] or 0,
                "married": user["married"] or 0,
                "child": user["child"] or 0,
                "points": user["points"] or 0,
                "updated_at": user["updated_at"].isoformat() if user["updated_at"] else None
            }

        return {
            "updates": updates,
            "removed": removed_ids,
            "serverLasttime": now.isoformat()
        }

@app.get('/explore_people_updated_dic_old')
async def get_updated_people_dic_old(since: str):
    with Session(engine) as session:
        stmt = select(User).where(User.updated_at > since)
        results = session.exec(stmt).all()

        # 创建用户字典，键为用户ID，值为用户对象
        people_dict = {}
        max_updated_at = None

        for user in results:
            # 将用户对象转换为字典
            user_dict = {
                'avatar': user.avatar,
                'birth_date': user.birth_date.isoformat() if user.birth_date else None,
                'education': user.education,
                'gender': user.gender,
                'height': user.height,
                'id': user.id,
                'income_level': user.income_level,
                'mem': user.mem,
                'nickname': user.nickname,
                'occupation': user.occupation,
                'photo': user.photo,
                'region_code': user.region_code,
                'weight': user.weight,
                'tip': float(user.tip) if user.tip else 0.0,
                'istop': user.istop or 0,
                'married': user.married or 0,
                'child': user.child or 0,
                'points': user.points or 0,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }

            # 添加到字典，键为ID
            people_dict[str(user.id)] = user_dict

            # 更新最大更新时间
            if user.updated_at:
                if max_updated_at is None or user.updated_at > max_updated_at:
                    max_updated_at = user.updated_at

        # 如果没有新数据，返回原始时间
        lasttime = max_updated_at.isoformat() if max_updated_at else since

        return {
            'people': people_dict,  # 返回字典格式
            'lasttime': lasttime
        }

@app.get('/explore_people_updated')
async def get_updated_people(since: str):
    with Session(engine) as session:
        stmt = select(User).where(User.updated_at > since)
        results = session.exec(stmt).all()
        return {
            'people': [dict(u) for u in results],
            'lasttime': max(u.updated_at for u in results)
        }

@app.get("/interested")
@cache(expire=300)
async def get_interested_users():
    try:
        # 创建子查询：获取所有置顶用户的ID
        subquery = select(UserTop.id).scalar_subquery()

        # 使用子查询直接查询User表
        stmt = select(User).where(User.id.in_(subquery))

        # 执行查询
        with Session(engine) as session:
            interested_users = session.scalars(stmt).all()

        # 格式化返回数据
        users_list = [
            user.model_dump(exclude={"openid", "phone", "mem_pri", "photo"})
            for user in interested_users
        ]

        return users_list

    except Exception as e:
        logger.error(f"获取感兴趣用户失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="获取感兴趣用户失败"
        )

@app.post("/visit-count")
async def get_visit_count(
    data: dict = Body(...),  # 使用 Body 自动解析 JSON
    openid: str = Depends(get_current_user)
):
    """获取来访数量（无时间过滤）"""
    target_user_id = data.get("user_id")

    with Session(engine) as session:
        if not target_user_id:
            user = session.exec(select(User.id).where(User.openid == openid)).first()
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            target_user_id = user

        # 移除了时间过滤条件
        count = session.scalar(
            text("""
                SELECT COUNT(*)
                FROM user_visits
                WHERE target_id = :target_id
                AND visitor_id != :target_id
            """),
            {"target_id": target_user_id}
        )

        return {"count": count}

@app.post("/visit-records")
async def get_visit_records(
    data: dict = Body(...),  # 使用 Body 自动解析 JSON
    openid: str = Depends(get_current_user)
):
    """获取来访明细记录（无时间过滤）"""
    target_user_id = data.get("user_id")

    with Session(engine) as session:
        if not target_user_id:
            user = session.exec(select(User.id).where(User.openid == openid)).first()
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            target_user_id = user

        # 移除了时间过滤条件
        records = session.exec(
            text("""
                SELECT
                    u.id,
                    u.nickname,
                    u.avatar,
                    uv.created_at
                FROM user_visits uv
                JOIN user u ON uv.visitor_id = u.id
                WHERE uv.target_id = :target_id
                ORDER BY uv.created_at DESC
                LIMIT 100
            """),
            {"target_id": target_user_id}
        ).mappings().all()

        formatted_records = []
        for record in records:
            formatted_records.append({
                "id": record["id"],
                "nickname": record["nickname"],
                "avatar": record["avatar"],
                "visited_at": record["created_at"].isoformat()
            })

        return {"records": formatted_records}

# 新增统计模型
class StatItem(BaseModel):
    id: int
    count: int = 0
    created_at: Optional[datetime] = None

class VisitChartData(BaseModel):
    date: str
    count: int

class VisitStatsResponse(BaseModel):
    chart_data: List[VisitChartData]
    top_list: List[StatItem]

class LikeStatsResponse(BaseModel):
    list: List[StatItem]

# 访问统计接口
@app.get("/stat/visited/{user_id}")
async def get_visited_stats(
    user_id: int,
    days: int = 7,
    openid: str = Depends(get_admin_user)
):
    with Session(engine) as session:
        # 获取最近7天的日期范围
        end_date = datetime.now(beijing_tz)
        start_date = end_date - timedelta(days=days-1)

        # 查询图表数据
        chart_query = text("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM user_visits
            WHERE target_id = :user_id
              AND created_at >= :start_date
              AND created_at < :end_date + INTERVAL 1 DAY
            GROUP BY DATE(created_at)
            ORDER BY date ASC
        """)
        chart_result = session.execute(chart_query, {
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date
        }).fetchall()

        # 填充缺失的日期
        date_counts = {row[0].strftime("%Y-%m-%d"): row[1] for row in chart_result}
        chart_data = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            chart_data.append(VisitChartData(
                date=date_str,
                count=date_counts.get(date_str, 0)
                ))
            current_date += timedelta(days=1)

        # 查询访问者排行榜
        top_query = text("""
            SELECT visitor_id as id, COUNT(*) as count
            FROM user_visits
            WHERE target_id = :user_id
              AND created_at >= :start_date
            GROUP BY visitor_id
            ORDER BY count DESC
            LIMIT 10
        """)
        top_result = session.execute(top_query, {
            "user_id": user_id,
            "start_date": start_date
        }).fetchall()

        top_list = [StatItem(id=row[0], count=row[1]) for row in top_result]

        return VisitStatsResponse(chart_data=chart_data, top_list=top_list)

# 被访统计接口
@app.get("/stat/visit/{user_id}")
async def get_visit_stats(
    user_id: int,
    days: int = 7,
    openid: str = Depends(get_admin_user)
):
    with Session(engine) as session:
        # 获取最近7天的日期范围
        end_date = datetime.now(beijing_tz)
        start_date = end_date - timedelta(days=days-1)

        # 查询图表数据
        chart_query = text("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM user_visits
            WHERE visitor_id = :user_id
              AND created_at >= :start_date
              AND created_at < :end_date + INTERVAL 1 DAY
            GROUP BY DATE(created_at)
            ORDER BY date ASC
        """)
        chart_result = session.execute(chart_query, {
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date
        }).fetchall()

        # 填充缺失的日期
        date_counts = {row[0].strftime("%Y-%m-%d"): row[1] for row in chart_result}
        chart_data = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            chart_data.append(VisitChartData(
                date=date_str,
                count=date_counts.get(date_str, 0)
                ))
            current_date += timedelta(days=1)

        # 查询被访问者排行榜
        top_query = text("""
            SELECT target_id as id, COUNT(*) as count
            FROM user_visits
            WHERE visitor_id = :user_id
              AND created_at >= :start_date
            GROUP BY target_id
            ORDER BY count DESC
            LIMIT 10
        """)
        top_result = session.execute(top_query, {
            "user_id": user_id,
            "start_date": start_date
        }).fetchall()

        top_list = [StatItem(id=row[0], count=row[1]) for row in top_result]

        return VisitStatsResponse(chart_data=chart_data, top_list=top_list)

# 点赞统计接口
@app.get("/stat/likes/{user_id}")
async def get_likes_stats(
    user_id: int,
    limit: int = 30,
    openid: str = Depends(get_admin_user)
):
    with Session(engine) as session:
        query = text("""
            SELECT liked_id as id, created_at
            FROM user_likes
            WHERE liker_id = :user_id
            ORDER BY created_at DESC
            LIMIT :limit
        """)
        result = session.execute(query, {
            "user_id": user_id,
            "limit": limit
        }).fetchall()

        return LikeStatsResponse(list=[
            StatItem(id=row[0], created_at=row[1]) for row in result
        ])

# 被赞统计接口
@app.get("/stat/liked/{user_id}")
async def get_liked_stats(
    user_id: int,
    limit: int = 30,
    openid: str = Depends(get_admin_user)
):
    with Session(engine) as session:
        query = text("""
            SELECT liker_id as id, created_at
            FROM user_likes
            WHERE liked_id = :user_id
            ORDER BY created_at DESC
            LIMIT :limit
        """)
        result = session.execute(query, {
            "user_id": user_id,
            "limit": limit
        }).fetchall()

        return LikeStatsResponse(list=[
            StatItem(id=row[0], created_at=row[1]) for row in result
        ])

# 审核列表
# 审核列表
@app.get("/admin/audit-list")
async def audit_list(
    keyword: str = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    openid: str = Depends(get_admin_user)
):
    offset = (page - 1) * pageSize
    with Session(engine) as session:
        base = select(UserTmp).where(UserTmp.state == 0,UserTmp.gender != None)
        if keyword:
            try:
                keyword_id = int(keyword)
                base = base.where(
                    (UserTmp.nickname.contains(keyword)) | (UserTmp.id == keyword_id)
                )
            except ValueError:
                base = base.where(UserTmp.nickname.contains(keyword))
        total = session.exec(select(func.count()).select_from(base)).one()
        users = session.exec(
            base.order_by(UserTmp.created_at.desc()).offset(offset).limit(pageSize)
        ).all()
        return {"list": [u.model_dump(exclude={"openid"}) for u in users], "total": total}

# 审核详情
@app.get("/admin/audit-detail/{user_id}")
async def audit_detail(
    user_id: str,
    _: str = Depends(get_admin_user)
):
    with Session(engine) as session:
        statement = select(UserTmp).where(UserTmp.id == user_id)
        user = session.exec(statement).first()
        if not user or user.state != 0:
            raise HTTPException(status_code=404, detail="记录不存在")
        return user.model_dump(exclude={"openid", "state"})

# 审核通过
@app.post("/admin/audit-pass/{user_id}")
async def audit_pass(
    user_id: str,
    openid: str = Depends(get_admin_user)
):
    with Session(engine) as session:
        with session.begin():
            tmp = session.exec(select(UserTmp).where(UserTmp.id == user_id)).first()
            if not tmp or tmp.state != 0:
                raise HTTPException(status_code=404, detail="记录不存在")

            data = tmp.model_dump(exclude={"id", "state"})
            user = session.exec(select(User).where(User.openid == tmp.openid)).first()
            if user:
                for k, v in data.items():
                    setattr(user, k, v)
                user.updated_at = datetime.now(beijing_tz)
            else:
                user = User(**data)
                session.add(user)

            tmp.state = 1
            return {"status": "success", "message": "已通过"}

class RejectRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)

@app.post("/admin/audit-reject/{user_tmp_id}")
async def audit_reject(
    user_tmp_id: str,
    req: RejectRequest,
    openid: str = Depends(get_admin_user)
):
    with Session(engine) as session:
        with session.begin():
            tmp = session.exec(select(UserTmp).where(UserTmp.id == user_tmp_id)).first()
            if not tmp or tmp.state != 0:
                raise HTTPException(status_code=404, detail="记录不存在或状态异常")

            # 插入驳回记录（默认未读）
            session.execute(
                text("""
                    INSERT INTO audit_rejections (user_tmp_id, reason, created_by)
                    VALUES (:uid, :reason, :admin)
                """),
                {"uid": user_tmp_id, "reason": req.reason.strip(), "admin": openid}
            )

            # 把 user_tmp.state 置为 2（已驳回）
            tmp.state = 2
            session.add(tmp)

        return {"status": "success", "message": "已驳回"}


@app.post("/user/rejection/mark-read")
async def mark_rejection_read(
    openid: str = Depends(get_current_user)
):
    with Session(engine) as session:
        # 1. 获取当前用户的 user_tmp.id
        tmp = session.exec(select(UserTmp).where(UserTmp.openid == openid)).first()
        if not tmp:
            raise HTTPException(status_code=404, detail="用户资料未找到")

        # 2. 标记该用户的驳回记录为已读
        result = session.execute(
            text("""
                UPDATE audit_rejections
                SET is_read = 1
                WHERE user_tmp_id = :uid AND is_read = 0
            """),
            {"uid": tmp.id}
        )
        session.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="未找到未读的驳回记录")

        return {"status": "success", "message": "已标记已读"}

@app.get("/user/rejection")
async def get_rejection_info(
    openid: str = Depends(get_current_user)
):
    """
    返回当前用户最新的驳回记录（未读优先）
    """
    with Session(engine) as session:
        # 找到 user_tmp 记录
        tmp = session.exec(select(UserTmp).where(UserTmp.openid == openid)).first()
        if not tmp:
            return {"has_rejection": False}

        rej = session.execute(
            text("""
                SELECT id, reason, created_at, is_read
                FROM audit_rejections
                WHERE user_tmp_id = :uid
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"uid": tmp.id}
        ).fetchone()

        if not rej:
            return {"has_rejection": False}

        return {
            "has_rejection": True,
            "reason": rej.reason,
            "created_at": rej.created_at.isoformat(),
            "is_read": bool(rej.is_read)
        }

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
            loop = asyncio.get_event_loop()
            loop.create_task(record_visit(user_id, current_user_id))

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
            logger.info(f"获取用户详情出错: {str(e)}")
            raise HTTPException(status_code=500, detail="服务器内部错误")


# 获取最近7天登录统计
@app.get("/admin/login-stats")
async def get_login_stats(
    days: int = 7,
    openid: str = Depends(get_admin_user)
):
    """
    获取最近days天的每日登录人数（基于 user_points_log.action='login'）
    """
    with Session(engine) as session:
        end_date = datetime.now(beijing_tz).date()
        start_date = end_date - timedelta(days=days - 1)

        query = text("""
            SELECT DATE(created_at) AS login_date, COUNT(DISTINCT user_id) AS count
            FROM user_points_log
            WHERE action = 'login'
              AND DATE(created_at) BETWEEN :start AND :end
            GROUP BY DATE(created_at)
            ORDER BY login_date ASC
        """)

        results = session.execute(query, {
            "start": start_date,
            "end": end_date
        }).fetchall()

        date_counts = {row[0]: row[1] for row in results}
        chart_data = []
        current_date = start_date

        while current_date <= end_date:
            chart_data.append({
                "date": current_date.strftime("%m-%d"),
                "count": date_counts.get(current_date, 0)
            })
            current_date += timedelta(days=1)

        return chart_data

# 获取打赏统计
@app.get("/admin/tip-stats")
async def get_tip_stats(
    openid: str = Depends(get_admin_user)
):
    """
    获取打赏统计信息（本周vs上周）
    """
    with Session(engine) as session:
        today = datetime.now(beijing_tz).date()

        # 本周范围（周一到周日）
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        # 上周范围
        last_week_start = week_start - timedelta(days=7)
        last_week_end = week_start - timedelta(days=1)

        # 查询本周打赏
        week_query = text("""
            SELECT COALESCE(SUM(amount), 0) as total
            FROM user_tips
            WHERE DATE(created_at) BETWEEN :start AND :end
        """)

        week_total = session.execute(week_query, {
            "start": week_start,
            "end": week_end
        }).scalar_one()

        # 查询上周打赏
        last_week_total = session.execute(week_query, {
            "start": last_week_start,
            "end": last_week_end
        }).scalar_one()

        # 计算环比增长率
        growth_rate = 0
        if last_week_total > 0:
            growth_rate = ((week_total - last_week_total) / last_week_total) * 100

        return {
            "total": float(week_total),
            "growth_rate": growth_rate,
            "last_week_total": float(last_week_total)
        }

# 获取最近注册人数（最近1个月缴费人数）
@app.get("/admin/new-registrations")
async def get_new_registrations(
    openid: str = Depends(get_admin_user)
):
    """
    获取最近1个月的缴费注册人数
    """
    with Session(engine) as session:
        end_date = datetime.now(beijing_tz).date()
        start_date = end_date - timedelta(days=30)

        query = text("""
            SELECT COUNT(DISTINCT openid) as count
            FROM user_recharge
            WHERE DATE(created_at) >= :start_date
        """)

        count = session.execute(query, {
            "start_date": start_date
        }).scalar_one()

        # 计算环比（对比上一个月）
        last_month_start = start_date - timedelta(days=30)
        last_month_count = session.execute(query, {
            "start_date": last_month_start
        }).scalar_one()

        growth_rate = 0
        if last_month_count > 0:
            growth_rate = ((count - last_month_count) / last_month_count) * 100

        return {
            "count": count,
            "growth_rate": growth_rate
        }

class SloganCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=255)

@app.post("/admin/slogan")
async def create_slogan(
    request: SloganCreate,
    openid: str = Depends(get_admin_user)
):
    with Session(engine) as session:
        session.execute(
            text("""
                INSERT INTO system_slogans (content, created_by)
                VALUES (:content, :created_by)
            """),
            {"content": request.content.strip(), "created_by": openid}
        )
        session.commit()
    return {"status": "success", "message": "标语已添加"}

# 获取最新标语
@app.get("/slogan-latest")
async def get_latest_slogan():
    with Session(engine) as session:
        slogan = session.exec(
            select(SystemSlogan).order_by(SystemSlogan.created_at.desc()).limit(1)
        ).first()

        if not slogan:
            return {"slogan": "欢迎来到天顺，祝您早日找到心仪的另一半！❤️"}

        return {"slogan": slogan.content}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)