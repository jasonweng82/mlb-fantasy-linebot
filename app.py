import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from yahoo_client import get_all_teams_stats
from analyzer import analyze_league, build_report, debug_report

app = Flask(__name__)

# LINE Bot API 初始化
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

LEAGUE_ID = os.getenv("YAHOO_LEAGUE_ID")

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"Webhook error: {e}")
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip().lower()

    # Debug 模式
    if text == "debug":
        all_players = get_all_teams_stats(LEAGUE_ID)
        reply = debug_report(all_players)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
        return

    # 今日 / 戰報
    if text in ["今日", "戰報"]:
        all_players = get_all_teams_stats(LEAGUE_ID)
        analysis = analyze_league(all_players)
        report = build_report(analysis)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=report)
        )
        return

    # 其他訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="請輸入『今日』或『戰報』，或輸入『debug』查看分析狀態。")
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
