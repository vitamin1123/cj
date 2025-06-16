from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import uvicorn
import hashlib
import hmac
import jwt
from sqlmodel import SQLModel, Field, create_engine, Session, select
from datetime import datetime, timedelta
from fastapi import Depends, Header
from pydantic import BaseModel, field_validator
from typing import Optional

app = FastAPI()

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
    openid: str = Field(primary_key=True)
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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

# 数据库连接
DATABASE_URL = "mysql+pymysql://root:1234%40Qazx@localhost/cj"
engine = create_engine(DATABASE_URL)

# 用户资料模型
class ProfileData(BaseModel):
    gender: str
    birth_date: datetime
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
    #redirect_url = f"http://localhost:5173/auth-success?token={token}"
    redirect_url = f"http://www.tianshunchenjie.com/auth-success?token={token}"
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

@app.get("/getprofile")
async def get_profile(
    openid: str = Depends(get_current_user)
):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.openid == openid)).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户资料未找到")
        return user.model_dump(exclude={"openid"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
