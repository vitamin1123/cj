from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import uvicorn
import hashlib
import hmac
from typing import Optional

app = FastAPI()



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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
