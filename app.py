import os
from flask import Flask, request, abort
from linebot.v3.messaging import MessagingApi, ApiClient, Configuration, PushMessageRequest, TextMessage
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from yahoo_client import get_all_teams_stats
from analyzer import analyze_league, build_report, debug_report

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
LEAGUE_ID = os.getenv("YAHOO_LEAGUE_ID")

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    print(f"📩 收到 webhook body: {body[:200]}")
    try:
        handler.handle(body, signature)
    except Exception as e:
        import traceback
        print(f"❌ Webhook error: {e}")
        print(traceback.format_exc())
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text.strip().lower()
    user_id = event.source.user_id

    with ApiClient(configuration) as api_client:
        line_api = MessagingApi(api_client)

        def push(msg):
            line_api.push_message(PushMessageRequest(
                to=user_id,
                messages=[TextMessage(type="text", text=msg)]
            ))

        # Debug 模式
        if text == "debug":
            push("⏳ Debug 資料抓取中，請稍候...")
            all_players = get_all_teams_stats(LEAGUE_ID, date="today")
            reply = debug_report(all_players) if all_players else "🚫 沒有資料"
            push(reply)
            return

        # 今日即時戰況
        if text in ["今日", "戰報"]:
            push("⏳ 資料抓取中，請稍候...")
            all_players = get_all_teams_stats(LEAGUE_ID, date="today")
            analysis = analyze_league(all_players)
            report = build_report(analysis)
            push(report)
            return

        # 昨日完整總結
        if text in ["昨日", "昨天"]:
            push("⏳ 資料抓取中，請稍候...")
            all_players = get_all_teams_stats(LEAGUE_ID, date="yesterday")
            analysis = analyze_league(all_players)
            report = build_report(analysis)
            push(report)
            return

        # 其他訊息
        push("請輸入『今日』或『戰報』查看即時戰況\n輸入『昨日』查看昨日完整總結\n輸入『debug』查看分析狀態")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
