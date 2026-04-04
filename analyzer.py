"""
球員表現分析器
"""
from datetime import datetime, timedelta

HOT_THRESHOLD  =  5.0
COLD_THRESHOLD = -2.0


def analyze_league(all_players: list) -> dict:
    if not all_players:
        return {"top2": [], "bottom2": [], "team_top3": [], "date": ""}

    played = [p for p in all_players if p["fpts"] != 0]
    if not played:
        played = all_players

    sorted_desc = sorted(played, key=lambda x: x["fpts"], reverse=True)
    sorted_asc  = sorted(played, key=lambda x: x["fpts"])

    # 計算各隊總得分
    team_scores = {}
    for p in all_players:
        t = p["team_name"]
        team_scores[t] = team_scores.get(t, 0) + p["fpts"]

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
        return "表現低迷 🥶"
    else:
        return "表現普通 😐"


def build_report(analysis: dict) -> str:
    if not analysis["top2"] and not analysis["bottom2"]:
        return "😴 今日沒有成績資料，可能是休賽日。"

    date_str = datetime.strptime(analysis["date"], "%Y-%m-%d").strftime("%Y/%m/%d")
    lines = [f"⚾ MLB Fantasy 聯盟每日戰報 {date_str}", ""]

    # 今日之星 TOP 2
    lines.append("🏆 今日之星 TOP 2")
    lines.append("─────────────")
    medals = ["🥇", "🥈"]
    for i, p in enumerate(analysis["top2"]):
        label = _performance_label(p["fpts"])
        lines.append(
            f"{medals[i]} {p['name']} ({p['position']}) 今天得了 {p['fpts']:+.1f} 分，{label} 所屬隊伍：{p['team_name']}"
        )
    lines.append("")

    # 今日崩潰 BOTTOM 2
    lines.append("😢 今日崩潰 BOTTOM 2")
    lines.append("─────────────")
    sad = ["😭", "😿"]
    for i, p in enumerate(analysis["bottom2"]):
        label = _performance_label(p["fpts"])
        lines.append(
            f"{sad[i]} {p['name']} ({p['position']}) 今天得了 {p['fpts']:+.1f} 分，{label} 所屬隊伍：{p['team_name']}"
        )
    lines.append("")

    # 隊伍得分 TOP 3
    lines.append("🏅 今日隊伍得分 TOP 3")
    lines.append("─────────────")
    team_medals = ["🥇", "🥈", "🥉"]
    for i, (team_name, score) in enumerate(analysis["team_top3"]):
        lines.append(f"{team_medals[i]} {team_name}：{score:+.1f} 分")

    return "\n".join(lines)


def debug_report(all_players: list) -> str:
    if not all_players:
        return "🚫 沒有抓到任何球員資料。"

    total_players = len(all_players)

    team_scores = {}
    for p in all_players:
        t = p["team_name"]
        team_scores[t] = team_scores.get(t, 0) + p["fpts"]

    team_top3 = sorted(team_scores.items(), key=lambda x: x[1], reverse=True)[:3]

    lines = [
        f"🔍 Debug 模式",
        f"📋 抓到 {total_players} 位球員",
        "🏅 隊伍得分 TOP3"
    ]
    for i, (team_name, score) in enumerate(team_top3):
        lines.append(f"{i+1}. {team_name}：{score:+.1f} 分")

    return "\n".join(lines)


def analyze_weekly(all_players: list) -> dict:
    if not all_players:
        return {}

    weekly_stats = {}
    for p in all_players:
        team = p["team_name"]
        if team not in weekly_stats:
            weekly_stats[team] = {
                "HR": 0, "BB": 0, "SB": 0, "K_bat": 0,
                "K_pitch": 0, "W": 0, "SV": 0, "ER": 0
            }

        weekly_stats[team]["HR"]      += p.get("HR", 0)
        weekly_stats[team]["BB"]      += p.get("BB", 0)
        weekly_stats[team]["SB"]      += p.get("SB", 0)
        weekly_stats[team]["K_bat"]   += p.get("K_bat", 0)
        weekly_stats[team]["K_pitch"] += p.get("K_pitch", 0)
        weekly_stats[team]["W"]       += p.get("W", 0)
        weekly_stats[team]["SV"]      += p.get("SV", 0)
        weekly_stats[team]["ER"]      += p.get("ER", 0)

    def top_team(key):
        return max(weekly_stats.items(), key=lambda x: x[1][key])

    return {
        "HR":      top_team("HR"),
        "BB":      top_team("BB"),
        "SB":      top_team("SB"),
        "K_bat":   top_team("K_bat"),
        "K_pitch": top_team("K_pitch"),
        "W":       top_team("W"),
        "SV":      top_team("SV"),
        "ER":      top_team("ER"),
    }


def build_weekly_report(weekly: dict, records: dict = None) -> str:
    if not weekly:
        return "📋 本週沒有成績資料。"

    lines = ["📊 MLB Fantasy 本週統計", ""]

    lines.append("🧢 打者")
    lines.append(f"💥 轟轟轟  {weekly['HR'][0]} 本週 {weekly['HR'][1]['HR']} HR" +
                 (" 🏆 破聯盟紀錄" if records and weekly['HR'][1]['HR'] > records.get('HR') else ""))
    lines.append(f"👀 選球眼  {weekly['BB'][0]} 本週 {weekly['BB'][1]['BB']} BB")
    lines.append(f"💨 盜盜盜  {weekly['SB'][0]} 本週 {weekly['SB'][1]['SB']} SB")
    lines.append(f"🍳 呷K少年家  {weekly['K_bat'][0]} 本週吞 {weekly['K_bat'][1]['K_bat']} K")
    lines.append("")

    lines.append("⚾ 投手")
    lines.append(f"🔥 三振槍  {weekly['K_pitch'][0]} 本週 {weekly['K_pitch'][1]['K_pitch']} K")
    lines.append(f"🏆 勝投王  {weekly['W'][0]} 本週 {weekly['W'][1]['W']} W")
    lines.append(f"🔒 終結者  {weekly['SV'][0]} 本週 {weekly['SV'][1]['SV']} SV")
    lines.append(f"🛢️ 油罐車  {weekly['ER'][0]} 本週掉 {weekly['ER'][1]['ER']} 分")

    return "\n".join(lines)
