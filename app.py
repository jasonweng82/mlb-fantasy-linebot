import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError

from yahoo_client import get_all_teams_stats
from analyzer import analyze_league, build_report

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
LEAGUE_ID = os.getenv("YAHOO_LEAGUE_ID")

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
        
    if text in ["今日", "戰報"]:
        all_players = get_all_teams_stats(LEAGUE_ID, date="today")
        analysis = analyze_league(all_players)
        report = build_report(analysis)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=report)
        )
        return
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
