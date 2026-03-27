"""
Yahoo Fantasy Baseball API 客戶端
直接用 requests 呼叫 Yahoo Fantasy API
"""
import json
import requests
from datetime import datetime, timedelta

BASE_URL = "https://fantasysports.yahooapis.com/fantasy/v2"


def _load_creds(token_file="oauth2.json"):
    with open(token_file) as f:
        return json.load(f)


def _get_headers(creds):
    return {
        "Authorization": "Bearer " + creds["access_token"],
        "Accept": "application/json",
    }


def _refresh_token(creds, token_file="oauth2.json"):
    resp = requests.post(
        "https://api.login.yahoo.com/oauth2/get_token",
        auth=(creds["consumer_key"], creds["consumer_secret"]),
        data={
            "grant_type": "refresh_token",
            "refresh_token": creds["refresh_token"],
        },
    )
    if resp.status_code == 200:
        new = resp.json()
        creds["access_token"]  = new["access_token"]
        creds["refresh_token"] = new.get("refresh_token", creds["refresh_token"])
        with open(token_file, "w") as f:
            json.dump(creds, f, indent=2)
        print("Token 已刷新")
    return creds


def _api_get(url, creds, token_file="oauth2.json"):
    resp = requests.get(url, headers=_get_headers(creds))
    if resp.status_code == 401:
        creds = _refresh_token(creds, token_file)
        resp = requests.get(url, headers=_get_headers(creds))
    resp.raise_for_status()
    return resp.json()


def _extract_pos(p_info):
    """從 p_info list 裡抓 selected_position 的 position 值"""
    for x in p_info:
        if not isinstance(x, dict):
            continue
        if "selected_position" not in x:
            continue
        sp = x["selected_position"]
        if not isinstance(sp, list):
            continue
        for item in sp:
            if isinstance(item, dict) and "position" in item:
                return item["position"]
    return "?"


def _extract_score(p_stats):
    """從 p_stats 抓 Fantasy 積分"""
    try:
        pp = p_stats.get("player_points", {})
        total = pp.get("total", None)
        if total not in (None, "-", ""):
            return round(float(total), 1)
    except (TypeError, ValueError):
        pass
    return 0.0


def get_all_teams_stats(league_id, date="yesterday", token_file="oauth2.json"):
    """
    date 參數：
      "yesterday" → 昨天（預設，GitHub Action 總結用）
      "today"     → 今天（LINE Bot 即時查詢用）
      "2026-03-25" → 指定日期
    """
    if date == "yesterday":
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    elif date == "today":
        target_date = datetime.now().strftime("%Y-%m-%d")
    else:
        target_date = date

    print(f"查詢日期：{target_date}")

    creds = _load_creds(token_file)
    all_players = []

    # Step 1: 取得所有隊伍
    print("取得聯盟隊伍清單...")
    url = BASE_URL + "/league/" + league_id + "/teams?format=json"
    data = _api_get(url, creds, token_file)

    try:
        teams_raw = data["fantasy_content"]["league"][1]["teams"]
        team_count = teams_raw["count"]
    except (KeyError, IndexError) as e:
        print("無法取得隊伍清單: " + str(e))
        return []

    team_keys = []
    team_meta = {}

    for i in range(team_count):
        t = teams_raw[str(i)]["team"][0]
        team_key  = next((x["team_key"] for x in t if isinstance(x, dict) and "team_key" in x), None)
        team_name = next((x["name"]     for x in t if isinstance(x, dict) and "name"     in x), "隊伍" + str(i))
        managers  = next((x["managers"] for x in t if isinstance(x, dict) and "managers" in x), [])
        manager   = managers[0]["manager"].get("nickname", "未知") if managers else "未知"
        if team_key:
            team_keys.append(team_key)
            team_meta[team_key] = {"team_name": team_name, "manager": manager}

    print("找到 " + str(len(team_keys)) + " 支隊伍")

    # Step 2: 每隊抓球員 + 指定日期得分
    for team_key in team_keys:
        meta = team_meta[team_key]
        url = (
            BASE_URL
            + "/team/" + team_key
            + "/roster/players/stats;type=date;date=" + target_date
            + "?format=json"
        )

        try:
            data = _api_get(url, creds, token_file)
            players_raw = data["fantasy_content"]["team"][1]["roster"]["0"]["players"]
            player_count = players_raw["count"]
        except Exception as e:
            print("無法取得 " + meta["team_name"] + " 成績: " + str(e))
            continue

        for j in range(player_count):
            try:
                p = players_raw[str(j)]["player"]
                p_info  = p[0]
                p_stats = p[1] if len(p) > 1 else {}

                # 球員名字
                name_dict = next(
                    (x["name"] for x in p_info if isinstance(x, dict) and "name" in x),
                    {}
                )
                name = name_dict.get("full", "未知") if isinstance(name_dict, dict) else "未知"

                # 守位
                pos = _extract_pos(p_info)

                if pos in ("BN", "IL", "NA"):
                    continue

                # 分數
                score = _extract_score(p_stats)

                all_players.append({
                    "team_name": meta["team_name"],
                    "manager":   meta["manager"],
                    "player":    name,
                    "position":  pos,
                    "score":     score,
                    "date":      target_date,
                })
            except Exception:
                continue

    print(f"共取得 {len(all_players)} 位球員的成績")
    return all_players


def _is_number(val):
    try:
        float(val)
        return True
    except (TypeError, ValueError):
        return False
