"""
LINE Messaging API 客戶端
負責將戰報推送到你的 LINE 帳號
"""
import os
import requests


LINE_API_URL = "https://api.line.me/v2/bot/message/push"


def push_message(text: str):
    """
    推送純文字訊息到指定的 LINE User ID
    需要環境變數：
      LINE_CHANNEL_ACCESS_TOKEN  — Messaging API 的 Channel Access Token
      LINE_USER_ID               — 你自己的 LINE User ID
    """
    token   = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    user_id = os.environ["LINE_USER_ID"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": text,
            }
        ],
    }

    resp = requests.post(LINE_API_URL, headers=headers, json=payload, timeout=10)

    if resp.status_code == 200:
        print("✅ LINE 推送成功")
    else:
        print(f"❌ LINE 推送失敗: {resp.status_code} {resp.text}")
        resp.raise_for_status()
