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
    all_players = get_all_teams_stats(LEAGUE_ID)

    if not all_players or len(all_players) == 0:
        reply = "⚾ 今日無成績"
    else:
        analysis = analyze_league(all_players)
        report = build_report(analysis)

        # 計算隊伍總分
        team_scores = {}
        for p in all_players:
            team = p["team"]
            fpts = p.get("fpts", 0)
            team_scores[team] = team_scores.get(team, 0) + fpts

        # 排序取 TOP3
        top3 = sorted(team_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        top3_text = "\n".join([f"{i+1}. {team} {score} pts" for i, (team, score) in enumerate(top3)])

        reply = f"{report}\n\n🏆 今日隊伍 TOP3\n{top3_text}"

    push_message(reply)

if __name__ == "__main__":
    main()
