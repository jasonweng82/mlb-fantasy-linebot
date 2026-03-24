"""
MLB Fantasy LINE Bot — 主程式
"""
import os
from dotenv import load_dotenv

from yahoo_client import get_all_teams_stats
from analyzer import analyze_league, build_report
from line_client import push_message
import os

LEAGUE_ID = os.getenv("YAHOO_LEAGUE_ID")

def main():
    # 抓取所有球員資料
    all_players = get_all_teams_stats(LEAGUE_ID)

    # 判斷是否有資料
    if not all_players or len(all_players) == 0:
        reply = "⚾ 今日無成績"
    else:
        analysis = analyze_league(all_players)
        reply = build_report(analysis)

    # 推送到 LINE
    push_message(reply)

if __name__ == "__main__":
    main()
