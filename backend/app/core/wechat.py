import httpx
from typing import Dict, Any

from app.core.config import settings


class WeChatClient:
    """微信 API 客户端"""

    def __init__(self):
        self.app_id = settings.WX_APP_ID
        self.app_secret = settings.WX_APP_SECRET

    async def code2session(self, code: str) -> Dict[str, Any]:
        """
        微信登录凭证校验
        https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html
        """
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": self.app_id,
            "secret": self.app_secret,
            "js_code": code,
            "grant_type": "authorization_code"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

        return data

    async def get_access_token(self) -> str:
        """
        获取小程序全局唯一后台接口调用凭据
        https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/access-token/auth.getAccessToken.html
        """
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

        if "access_token" not in data:
            raise Exception(f"获取 access_token 失败: {data}")

        return data["access_token"]

    async def send_subscribe_message(
        self,
        openid: str,
        template_id: str,
        data: Dict[str, Any],
        page: str = "pages/index/index"
    ):
        """
        发送订阅消息
        https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/subscribe-message/subscribeMessage.send.html
        """
        access_token = await self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}"

        payload = {
            "touser": openid,
            "template_id": template_id,
            "page": page,
            "data": data,
            "miniprogram_state": "formal"  # developer/trial/formal
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            result = response.json()

        return result


# 全局微信客户端
wechat_client = WeChatClient()
