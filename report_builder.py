from typing import Optional


def build_daily_report_flex(data: dict) -> dict:
    """
    將戰報資料組成 LINE Flex Message (Bubble)
    """
    date = data["date"]
    hot = data["hot"]
    cold = data["cold"]
    total_fpts = data["total_fpts"]
    player_count = data["player_count"]

    trend = "📈" if total_fpts >= 30 else ("📉" if total_fpts < 10 else "➡️")
    score_color = "#22c55e" if total_fpts >= 30 else ("#ef4444" if total_fpts < 10 else "#f59e0b")

    # ── Header ──────────────────────────────────────────────
    header = {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": "#1a1a2e",
        "paddingAll": "20px",
        "contents": [
            {
                "type": "text",
                "text": "⚾  MLB FANTASY",
                "color": "#e2b96f",
                "size": "xs",
                "weight": "bold",
                "letterSpacing": "3px"
            },
            {
                "type": "text",
                "text": "每日戰報",
                "color": "#ffffff",
                "size": "xxl",
                "weight": "bold",
                "margin": "xs"
            },
            {
                "type": "text",
                "text": date,
                "color": "#8888aa",
                "size": "sm",
                "margin": "xs"
            }
        ]
    }

    # ── 總積分 ──────────────────────────────────────────────
    score_box = {
        "type": "box",
        "layout": "horizontal",
        "backgroundColor": "#0f0f23",
        "paddingAll": "16px",
        "contents": [
            {
                "type": "box",
                "layout": "vertical",
                "flex": 1,
                "contents": [
                    {"type": "text", "text": "今日總積分", "color": "#8888aa", "size": "xs"},
                    {
                        "type": "text",
                        "text": f"{trend} {total_fpts} pts",
                        "color": score_color,
                        "size": "xl",
                        "weight": "bold"
                    }
                ]
            },
            {
                "type": "box",
                "layout": "vertical",
                "flex": 1,
                "contents": [
                    {"type": "text", "text": "出賽人數", "color": "#8888aa", "size": "xs", "align": "end"},
                    {
                        "type": "text",
                        "text": f"👥 {player_count} 人",
                        "color": "#ccccee",
                        "size": "lg",
                        "weight": "bold",
                        "align": "end"
                    }
                ]
            }
        ]
    }

    body_contents = [score_box, _separator()]

    # ── 🔥 表現亮眼 ─────────────────────────────────────────
    if hot:
        body_contents.append(_section_header("🔥  表現亮眼", "#ff6b35"))
        for p in hot:
            body_contents.append(_player_row(p, "hot"))
        body_contents.append(_separator())

    # ── 😔 表現低迷 ─────────────────────────────────────────
    if cold:
        body_contents.append(_section_header("🧊  表現低迷", "#60a5fa"))
        for p in cold:
            body_contents.append(_player_row(p, "cold"))
        body_contents.append(_separator())

    # ── Footer ──────────────────────────────────────────────
    footer_text = "👍 繼續加油！" if total_fpts >= 30 else ("💪 明天再拼！" if total_fpts < 10 else "⚾ 持續觀察中")
    body_contents.append({
        "type": "text",
        "text": footer_text,
        "color": "#8888aa",
        "size": "xs",
        "align": "center",
        "margin": "md"
    })

    return {
        "type": "bubble",
        "size": "kilo",
        "header": header,
        "body": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#16213e",
            "paddingAll": "0px",
            "contents": body_contents
        },
        "styles": {
            "header": {"backgroundColor": "#1a1a2e"},
            "body": {"backgroundColor": "#16213e"}
        }
    }


def _section_header(title: str, color: str) -> dict:
    return {
        "type": "box",
        "layout": "vertical",
        "paddingStart": "16px",
        "paddingEnd": "16px",
        "paddingTop": "12px",
        "paddingBottom": "4px",
        "contents": [
            {
                "type": "text",
                "text": title,
                "color": color,
                "size": "sm",
                "weight": "bold"
            }
        ]
    }


def _player_row(player: dict, grade: str) -> dict:
    name = player["name"]
    pos = player["position"]
    key_stats = player["key_stats"]
    fpts = player["fpts"]

    fpts_color = "#22c55e" if fpts > 0 else "#ef4444"
    fpts_str = f"+{fpts}" if fpts > 0 else str(fpts)
    pos_colors = {
        "SP": "#f59e0b", "RP": "#f97316", "P": "#f97316",
        "C": "#a78bfa", "1B": "#60a5fa", "2B": "#34d399",
        "3B": "#f472b6", "SS": "#fb923c", "OF": "#38bdf8",
        "DH": "#e879f9",
    }
    pos_color = pos_colors.get(pos, "#94a3b8")

    return {
        "type": "box",
        "layout": "horizontal",
        "paddingStart": "16px",
        "paddingEnd": "16px",
        "paddingTop": "8px",
        "paddingBottom": "8px",
        "contents": [
            # 守位標籤
            {
                "type": "box",
                "layout": "vertical",
                "width": "36px",
                "justifyContent": "center",
                "contents": [
                    {
                        "type": "text",
                        "text": pos,
                        "color": pos_color,
                        "size": "xxs",
                        "weight": "bold",
                        "align": "center"
                    }
                ]
            },
            # 球員名稱 + 成績
            {
                "type": "box",
                "layout": "vertical",
                "flex": 1,
                "contents": [
                    {"type": "text", "text": name, "color": "#e2e8f0", "size": "sm", "weight": "bold"},
                    {"type": "text", "text": key_stats, "color": "#94a3b8", "size": "xxs", "margin": "xs"}
                ]
            },
            # Fantasy 積分
            {
                "type": "text",
                "text": f"{fpts_str} pts",
                "color": fpts_color,
                "size": "sm",
                "weight": "bold",
                "align": "end",
                "gravity": "center"
            }
        ]
    }


def _separator() -> dict:
    return {
        "type": "box",
        "layout": "vertical",
        "margin": "none",
        "contents": [{"type": "separator", "color": "#2d2d5e"}]
    }
