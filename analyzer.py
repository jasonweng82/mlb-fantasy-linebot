"""
球員表現分析器
直接用 Yahoo 回傳的實際得分排名，找出全聯盟今日前2名與後2名
"""
from datetime import datetime, timedelta

# 幾分以上算「亮眼」、幾分以下算「低迷」（用於標籤文字）
HOT_THRESHOLD  =  5.0
COLD_THRESHOLD = -2.0


def analyze_league(all_players: list) -> dict:
    """
    輸入：get_all_teams_stats() 回傳的球員清單
    輸出：
    {
        "top2":    [最高分的前2位],
        "bottom2": [最低分的後2位],
        "date":    "2026-03-21",
    }
    """
    if not all_players:
        return {"top2": [], "bottom2": [], "date": ""}

    # 只看有實際上場、得分不為 0 的球員（過濾掉休息日空值）
    played = [p for p in all_players if p["score"] != 0]

    if not played:
        played = all_players  # 若全部都是 0，保留原始資料

    sorted_desc = sorted(played, key=lambda x: x["score"], reverse=True)
    sorted_asc  = sorted(played, key=lambda x: x["score"])

    return {
        "top2":    sorted_desc[:2],
        "bottom2": sorted_asc[:2],
        "date":    all_players[0]["date"],
    }


def _performance_label(score: float) -> str:
    if score >= HOT_THRESHOLD:
        return "表現亮眼 🔥"
    elif score <= COLD_THRESHOLD:
        return "表現低迷 😔"
    else:
        return "表現普通 📋"


def build_report(analysis: dict) -> str:
    """
    把分析結果組成 LINE 訊息
    格式：某某某的 XXX 今天得了 OO 分，表現亮眼
    """
    if not analysis["top2"] and not analysis["bottom2"]:
        return "⚾ 今日沒有成績資料，可能是休賽日。"

    date_str = datetime.strptime(analysis["date"], "%Y-%m-%d").strftime("%Y/%m/%d")

    lines = [
        f"⚾ MLB Fantasy 聯盟每日戰報 {date_str}",
        "",
    ]

    # ── 今日之星（前2名）──────────────────────────
    lines.append("🏆 今日之星 TOP 2")
    lines.append("━━━━━━━━━━━━━━")
    for i, p in enumerate(analysis["top2"], 1):
        medal = "🥇" if i == 1 else "🥈"
        label = _performance_label(p["score"])
        lines.append(
            f"{medal} {p['manager']} 的 {p['player']} ({p['position']})"
        )
        lines.append(
            f"    今天得了 {p['score']:+.1f} 分，{label}"
        )
        lines.append(f"    所屬隊伍：{p['team_name']}")
    lines.append("")

    # ── 今日最慘（後2名）──────────────────────────
    lines.append("💀 今日最慘 BOTTOM 2")
    lines.append("━━━━━━━━━━━━━━")
    for i, p in enumerate(analysis["bottom2"], 1):
        medal = "😭" if i == 1 else "😢"
        label = _performance_label(p["score"])
        lines.append(
            f"{medal} {p['manager']} 的 {p['player']} ({p['position']})"
        )
        lines.append(
            f"    今天得了 {p['score']:+.1f} 分，{label}"
        )
        lines.append(f"    所屬隊伍：{p['team_name']}")

    return "\n".join(lines)
