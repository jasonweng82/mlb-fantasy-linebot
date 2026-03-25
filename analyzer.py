"""
球員表現分析器
"""
from datetime import datetime, timedelta

HOT_THRESHOLD  =  5.0
COLD_THRESHOLD = -2.0


def analyze_league(all_players: list) -> dict:
    if not all_players:
        return {"top2": [], "bottom2": [], "team_top3": [], "date": ""}

    played = [p for p in all_players if p["score"] != 0]
    if not played:
        played = all_players

    sorted_desc = sorted(played, key=lambda x: x["score"], reverse=True)
    sorted_asc  = sorted(played, key=lambda x: x["score"])

    # 計算各隊總得分
    team_scores = {}
    for p in all_players:
        t = p["team_name"]
        team_scores[t] = team_scores.get(t, 0) + p["score"]

    team_top3 = sorted(team_scores.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        "top2":      sorted_desc[:2],
        "bottom2":   sorted_asc[:2],
        "team_top3": team_top3,
        "date":      all_players[0]["date"],
    }


def _performance_label(score: float) -> str:
    if score >= HOT_THRESHOLD:
        return "表現亮眼 🔥"
    elif score <= COLD_THRESHOLD:
        return "表現低迷 😔"
    else:
        return "表現普通 📋"


def build_report(analysis: dict) -> str:
    if not analysis["top2"] and not analysis["bottom2"]:
        return "⚾ 今日沒有成績資料，可能是休賽日。"

    date_str = datetime.strptime(analysis["date"], "%Y-%m-%d").strftime("%Y/%m/%d")
    lines = [f"⚾ MLB Fantasy 聯盟每日戰報 {date_str}", ""]

    # 今日之星 TOP 2
    lines.append("🏆 今日之星 TOP 2")
    lines.append("━━━━━━━━━━━━━━")
    medals = ["🥇", "🥈"]
    for i, p in enumerate(analysis["top2"]):
        label = _performance_label(p["score"])
        lines.append(
            f"{medals[i]} {p['player']} ({p['position']}) 今天得了 {p['score']:+.1f} 分，{label} 所屬隊伍：{p['team_name']}－{p['manager']}"
        )
    lines.append("")

    # 今日最慘 BOTTOM 2
    lines.append("💀 今日最慘 BOTTOM 2")
    lines.append("━━━━━━━━━━━━━━")
    sad = ["😭", "😢"]
    for i, p in enumerate(analysis["bottom2"]):
        label = _performance_label(p["score"])
        lines.append(
            f"{sad[i]} {p['player']} ({p['position']}) 今天得了 {p['score']:+.1f} 分，{label} 所屬隊伍：{p['team_name']}－{p['manager']}"
        )
    lines.append("")

    # 隊伍得分 TOP 3
    lines.append("🏅 今日隊伍得分 TOP 3")
    lines.append("━━━━━━━━━━━━━━")
    team_medals = ["🥇", "🥈", "🥉"]
    for i, (team_name, score) in enumerate(analysis["team_top3"]):
        lines.append(f"{team_medals[i]} {team_name}：{score:+.1f} 分")

    return "\n".join(lines)
def debug_report(all_players: list) -> str:
    if not all_players:
        return "⚾ 沒有抓到任何球員資料。"

    total_players = len(all_players)

    # 計算隊伍總分
    team_scores = {}
    for p in all_players:
        t = p["team_name"]
        team_scores[t] = team_scores.get(t, 0) + p["score"]

    # 排序取 TOP3
    team_top3 = sorted(team_scores.items(), key=lambda x: x[1], reverse=True)[:3]

    # 組合訊息
    lines = [
        f"🔍 Debug 模式",
        f"📊 抓到 {total_players} 位球員",
        "🏅 隊伍得分 TOP3"
    ]
    for i, (team_name, score) in enumerate(team_top3):
        lines.append(f"{i+1}. {team_name}：{score:+.1f} 分")

    return "\n".join(lines)
