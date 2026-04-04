"""
MLB Fantasy LINE Bot - 主程式
"""
import os
from dotenv import load_dotenv

from yahoo_client import get_all_teams_stats
from analyzer import analyze_league, build_report
from line_client import push_message

load_dotenv()
LEAGUE_ID = os.environ["YAHOO_LEAGUE_ID"]

def main():
    print("🚀 開始執行 MLB Fantasy 戰報...")

    print("📋 抓取聯盟所有球員成績...")
    all_players = get_all_teams_stats(LEAGUE_ID)

    if not all_players:
        push_message("🚫 昨日沒有成績資料，可能是休賽日。")
        return

    print(f"✅ 共取得 {len(all_players)} 位球員的成績")

    analysis = analyze_league(all_players)

    # Debug：確認 team_top3 有正確產生
    print(f"🏆 team_top3: {analysis['team_top3']}")

    report = build_report(analysis)

    print("\n" + "="*40)
    print(report)
    print("="*40 + "\n")

    push_message(report)
    print("✅ 完成！")

if __name__ == "__main__":
    main()
