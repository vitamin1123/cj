from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import hashlib
import requests
import uvicorn
from urllib.parse import quote
import os

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 微信配置
WECHAT_CONFIG = {
    "token": "your_token_here",  # 在微信公众平台设置的Token
    "app_id": "your_app_id_here",  # 微信公众号的AppID
    "app_secret": "your_app_secret_here",  # 微信公众号的AppSecret
}

# 微信服务器验证
@app.get("/wechat")
async def wechat_verify(signature: str, timestamp: str, nonce: str, echostr: str):
    """
    微信服务器验证接口
    """
    token = WECHAT_CONFIG["token"]
    
    # 将token、timestamp、nonce三个参数进行字典序排序
    tmp_arr = [token, timestamp, nonce]
    tmp_arr.sort()
    tmp_str = "".join(tmp_arr)
    
    # 进行sha1加密
    tmp_str = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
    
    # 验证签名
    if tmp_str == signature:
        return PlainTextResponse(echostr)
    else:
        raise HTTPException(status_code=403, detail="验证失败")

# 获取微信access_token
async def get_access_token():
    """
    获取微信access_token
    """
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WECHAT_CONFIG['app_id']}&secret={WECHAT_CONFIG['app_secret']}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "access_token" in data:
            return data["access_token"]
        else:
            print(f"获取access_token失败: {data}")
            return None
    except Exception as e:
        print(f"获取access_token异常: {e}")
        return None

# 微信网页授权 - 获取授权URL
@app.get("/wechat/auth_url")
async def get_auth_url(redirect_uri: str):
    """
    获取微信网页授权URL
    """
    encoded_redirect_uri = quote(redirect_uri)
    auth_url = f"https://open.weixin.qq.com/connect/oauth2/authorize?appid={WECHAT_CONFIG['app_id']}&redirect_uri={encoded_redirect_uri}&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect"
    
    return {"auth_url": auth_url}

# 通过code获取openid和用户信息
@app.get("/wechat/user_info")
async def get_user_info(code: str):
    """
    通过微信授权code获取用户信息
    """
    try:
        # 第一步：通过code获取access_token和openid
        token_url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={WECHAT_CONFIG['app_id']}&secret={WECHAT_CONFIG['app_secret']}&code={code}&grant_type=authorization_code"
        
        token_response = requests.get(token_url)
        token_data = token_response.json()
        
        if "access_token" not in token_data:
            raise HTTPException(status_code=400, detail=f"获取access_token失败: {token_data}")
        
        access_token = token_data["access_token"]
        openid = token_data["openid"]
        
        # 第二步：通过access_token和openid获取用户信息
        user_info_url = f"https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={openid}&lang=zh_CN"
        
        user_response = requests.get(user_info_url)
        user_data = user_response.json()
        
        if "errcode" in user_data:
            raise HTTPException(status_code=400, detail=f"获取用户信息失败: {user_data}")
        
        return {
            "openid": openid,
            "nickname": user_data.get("nickname", ""),
            "headimgurl": user_data.get("headimgurl", ""),
            "sex": user_data.get("sex", 0),
            "province": user_data.get("province", ""),
            "city": user_data.get("city", ""),
            "country": user_data.get("country", "")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息异常: {str(e)}")

# 测试接口
@app.get("/test")
async def test():
    return {"message": "微信服务正常运行"}

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)