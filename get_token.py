"""
Yahoo OAuth Token 取得工具
手動交換 token 版本，相容所有版本
"""
import json
import requests
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth

CLIENT_ID     = "dj0yJmk9Z2hhOUdjVndEUlVWJmQ9WVdrOVFtdHdlRWN6WW00bWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWI2"
CLIENT_SECRET = "9a8314a04305fcbcac7d0d146bc2695c1f360a6d"
REDIRECT_URI  = "https://localhost:8080/callback"

AUTH_URL  = "https://api.login.yahoo.com/oauth2/request_auth"
TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"


def main():
    # Step 1: 產生授權網址
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    auth_url, state = oauth.authorization_url(AUTH_URL)

    print("=" * 60)
    print("請用瀏覽器開啟以下網址，登入 Yahoo 並同意授權：")
    print()
    print(auth_url)
    print()
    print("授權後瀏覽器會跳到一個無法開啟的頁面，")
    print("請複製網址列的完整網址貼到這裡：")
    print("=" * 60)

    redirect_response = input("貼上完整網址：").strip()

    # Step 2: 用授權碼換 token
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, state=state)

    import os
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    token = oauth.fetch_token(
        TOKEN_URL,
        authorization_response=redirect_response,
        auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
    )

    # Step 3: 存成 oauth2.json
    with open("oauth2.json", "w") as f:
        json.dump({
            "consumer_key":    CLIENT_ID,
            "consumer_secret": CLIENT_SECRET,
            "access_token":    token["access_token"],
            "refresh_token":   token["refresh_token"],
            "token_type":      token["token_type"],
        }, f, indent=2)

    print()
    print("✅ oauth2.json 已儲存！可以執行 main.py 了")


if __name__ == "__main__":
    main()
