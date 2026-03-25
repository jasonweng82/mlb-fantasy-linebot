import os
from yahoo_client import get_all_teams_stats
from analyzer import analyze_weekly, build_weekly_report
from line_client import push_message

LEAGUE_ID = os.getenv("YAHOO_LEAGUE_ID")

def main():
    print("📅 開始執行 MLB Fantasy 本週統計...")
    all_players = get_all_teams_stats(LEAGUE_ID)

    weekly = analyze_weekly(all_players)
    report = build_weekly_report(weekly)

    print(report)
    push_message(report)
    print("✅ 完成！")

if __name__ == "__main__":
    main()
