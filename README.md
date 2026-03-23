# ⚾ MLB Fantasy LINE Bot

每天自動推送 Yahoo Fantasy Baseball 戰報到你的 LINE！

## 📋 前置作業

### 1. 申請 Yahoo Developer 帳號
1. 前往 https://developer.yahoo.com/apps/create/
2. 建立新 App：
   - App Name: `MLB Fantasy Bot`（隨便取）
   - App Type: `Installed Application`
   - API Permissions: 勾選 `Fantasy Sports` → `Read`
3. 記下 **Client ID** 和 **Client Secret**

### 2. 申請 LINE Messaging API
1. 前往 https://developers.line.biz/
2. 建立 Provider → 建立 Messaging API Channel
3. 在 Channel 設定頁面取得 **Channel Access Token**（長期）
4. 取得你的 **LINE User ID**：
   - 掃描 QR code 加入你自己的 Bot
   - 在 LINE Official Account Manager 的 Webhook 日誌中可以看到 User ID
   - 或使用 https://api.line.me/v2/profile 查詢

### 3. 找到你的 Yahoo Fantasy 聯盟 ID
- 開啟 Yahoo Fantasy Baseball 網頁
- URL 格式：`https://baseball.fantasysports.yahoo.com/b1/XXXXX`
- 完整 League ID 格式為：`431.l.XXXXX`（431 是 MLB 的 game key）

---

## 🚀 本地安裝與測試

```bash
# 1. 安裝套件
pip install -r requirements.txt

# 2. 設定環境變數
cp .env.example .env
# 編輯 .env 填入你的金鑰

# 3. 編輯 get_token.py，填入 Yahoo Client ID/Secret
# 然後執行 OAuth 認證
python get_token.py
# 依照指示完成授權，會產生 token.json

# 4. 測試執行
python main.py
```

---

## ☁️ 部署到 Render

1. 把這個專案推上 GitHub（**注意：不要上傳 .env 和 token.json！**）
2. 前往 https://render.com 建立帳號
3. New → Cron Job → 連接你的 GitHub Repo
4. 設定環境變數（Environment Variables）：
   - `YAHOO_LEAGUE_ID`
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_USER_ID`
5. 上傳 `token.json` 到 Render（或使用 Render Secret Files 功能）
6. 部署完成！每天台灣時間早上 9:00 自動推送

---

## 📲 推送訊息範例

```
⚾ MLB Fantasy 每日戰報 2026/03/22

🔥 表現亮眼
━━━━━━━━━━━━━━
✅ Shohei Ohtani (OF) — 3/4, 2HR, 5RBI ⭐
✅ Freddie Freeman (1B) — 2/3, 1HR, 1BB

😔 表現低迷
━━━━━━━━━━━━━━
❌ Gerrit Cole (SP) — 4.0IP, 6ER, 2BB

📋 正常發揮：Juan Soto、Mookie Betts

📈 今日 Fantasy 得分貢獻：+24.5 pts
```

---

## 🗂 檔案說明

| 檔案 | 說明 |
|------|------|
| `main.py` | 主程式入口 |
| `yahoo_client.py` | Yahoo Fantasy API 串接 |
| `analyzer.py` | 球員表現分析與訊息產生 |
| `line_client.py` | LINE 推送 |
| `get_token.py` | 第一次 OAuth 認證工具 |
| `render.yaml` | Render 部署設定 |
