import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

import yahoo_fantasy_api as yfa
from yahoo_oauth import OAuth2

logger = logging.getLogger(__name__)

class YahooFantasyClient:
    """
    Yahoo Fantasy Baseball API 封裝
    負責取得你的 Fantasy 隊伍球員成績
    """

    def __init__(self):
    oauth_data = {
        "consumer_key": os.environ["YAHOO_CONSUMER_KEY"],
        "consumer_secret": os.environ["YAHOO_CONSUMER_SECRET"],
        "access_token": os.environ["YAHOO_TOKEN"],
        "refresh_token": os.environ.get("YAHOO_TOKEN_SECRET", ""),
        "token_type": "bearer",
    }

    with open("/tmp/oauth2.json", "w") as f:
        json.dump(oauth_data, f)

    sc = OAuth2(None, None, from_file="/tmp/oauth2.json")
    self.gm = yfa.Game(sc, "mlb")

    league_ids = self.gm.league_ids()
    if not league_ids:
        raise ValueError("找不到 Yahoo Fantasy Baseball 聯盟，請確認帳號有加入聯盟")

    league_id = os.environ.get("YAHOO_LEAGUE_ID", league_ids[0])
    self.league = self.gm.to_league(league_id)
    logger.info(f"✅ 成功連線聯盟: {league_id}")

    def get_all_teams_stats(self, league_id: str = None, date: str = "yesterday") -> Optional[list]:
        """
        取得聯盟所有隊伍、所有球員成績
        回傳 list of player dicts
        """
        if date == "today":
            target = datetime.now()
        else:
            target = datetime.now() - timedelta(days=1)

        date_str = target.strftime("%Y-%m-%d")
        logger.info(f"📅 查詢日期: {date_str}")

        all_players = []

        try:
            teams = self.league.teams()
            logger.info(f"共找到 {len(teams)} 支隊伍")

            for team_key, team_info in teams.items():
                team_name = team_info.get("name", team_key)
                logger.info(f"🔍 處理隊伍: {team_name} ({team_key})")

                try:
                    team = self.league.to_team(team_key)
                    roster = team.roster(day=target)
                except Exception as e:
                    logger.warning(f"⚠️ 無法取得 {team_name} 名單: {e}")
                    continue

                if not roster:
                    logger.warning(f"⚠️ {team_name} 名單為空")
                    continue

                for player in roster:
                    player_id = player.get("player_id") or player.get("id")
                    name = player.get("name")
                    position = player.get("selected_position", "BN")

                    if position == "BN":
                        continue

                    if not player_id or not name:
                        continue

                    stats = self._get_player_stats(player_id, date_str, name, position)
                    if stats:
                        stats["team_name"] = team_name
                        stats["team_key"] = team_key
                        stats["date"] = date_str
                        all_players.append(stats)

        except Exception as e:
            logger.error(f"❌ 取得所有隊伍失敗: {e}", exc_info=True)
            return None

        logger.info(f"✅ 共取得 {len(all_players)} 位球員成績")
        return all_players

    def get_yesterday_stats(self) -> Optional[list]:
        return self.get_all_teams_stats(date="yesterday")

    def _get_player_stats(self, player_id, date_str: str, name: str, position: str) -> Optional[dict]:
        try:
            pid = str(player_id)
            stats_raw = self.league.player_stats([pid], "date", date=date_str)

            if not stats_raw:
                return None

            raw = stats_raw[0] if isinstance(stats_raw, list) else stats_raw
            stat_map = raw.get("stats") or raw.get("stat") or {}

            if isinstance(stat_map, list):
                stat_map = {s.get("stat_id"): s.get("value", 0) for s in stat_map}

            is_pitcher = position in ["SP", "RP", "P"]

            if is_pitcher:
                return self._score_pitcher(name, position, stat_map)
            else:
                return self._score_batter(name, position, stat_map)

        except Exception as e:
            logger.warning(f"⚠️ 無法取得 {name} 的成績: {e}")
            return None

    def _score_batter(self, name: str, position: str, stats: dict) -> dict:
        """野手評分（依你的聯盟計分）"""
        r    = float(stats.get("R", 0))
        b1   = float(stats.get("1B", 0))
        b2   = float(stats.get("2B", 0))
        b3   = float(stats.get("3B", 0))
        hr   = float(stats.get("HR", 0))
        rbi  = float(stats.get("RBI", 0))
        sb   = float(stats.get("SB", 0))
        cs   = float(stats.get("CS", 0))
        bb   = float(stats.get("BB", 0))
        hbp  = float(stats.get("HBP", 0))
        so   = float(stats.get("SO", 0))
        gidp = float(stats.get("GIDP", 0))

        fpts = (
            (r    *  1.0) +
            (b1   *  2.6) +
            (b2   *  5.2) +
            (b3   *  7.8) +
            (hr   * 10.4) +
            (rbi  *  1.0) +
            (sb   *  3.5) +
            (cs   * -0.5) +
            (bb   *  2.6) +
            (hbp  *  2.6) +
            (so   * -0.5) +
            (gidp * -1.0)
        )

        ab = float(stats.get("AB", 0))
        hits = b1 + b2 + b3 + hr
        avg = f"{hits/ab:.3f}" if ab > 0 else ".000"

        key_stats = f"{int(hits)}/{int(ab)} {avg}"
        if hr > 0:
            key_stats += f", {int(hr)}HR"
        if rbi > 0:
            key_stats += f", {int(rbi)}RBI"
        if sb > 0:
            key_stats += f", {int(sb)}SB"
        if bb > 0:
            key_stats += f", {int(bb)}BB"
        if hbp > 0:
            key_stats += f", {int(hbp)}HBP"

        grade = "hot" if fpts >= 8 else ("cold" if fpts <= 0 and ab >= 3 else "normal")

        return {
            "name": name,
            "position": position,
            "key_stats": key_stats,
            "fpts": round(fpts, 1),
            "grade": grade,
            "type": "batter",
        }

    def _score_pitcher(self, name: str, position: str, stats: dict) -> dict:
        """投手評分（依你的聯盟計分）"""
        w    = float(stats.get("W", 0))
        sv   = float(stats.get("SV", 0))
        out  = float(stats.get("OUT", 0))
        h    = float(stats.get("H", 0))
        er   = float(stats.get("ER", 0))
        bb   = float(stats.get("BB", 0))
        hbp  = float(stats.get("HBP", 0))
        k    = float(stats.get("K", 0))
        gidp = float(stats.get("GIDP", 0))
        hld  = float(stats.get("HLD", 0))
        qs   = float(stats.get("QS", 0))

        if out == 0 and stats.get("IP"):
            ip = float(stats.get("IP", 0))
            out = ip * 3

        if out == 0:
            return None

        fpts = (
            (w    *  3.0) +
            (sv   *  6.0) +
            (out  *  1.0) +
            (h    * -1.3) +
            (er   * -2.5) +
            (bb   * -1.3) +
            (hbp  * -1.3) +
            (k    *  2.0) +
            (gidp *  1.0) +
            (hld  *  5.0) +
            (qs   *  6.0)
        )

        ip_display = out / 3
        key_stats = f"{ip_display:.1f}IP, {int(k)}K"
        if w:
            key_stats += ", W"
        if sv:
            key_stats += ", SV"
        if hld:
            key_stats += ", HLD"
        if qs:
            key_stats += ", QS"
        if er > 0:
            key_stats += f", {int(er)}ER"

        grade = "hot" if fpts >= 12 else ("cold" if er >= 4 else "normal")

        return {
            "name": name,
            "position": position,
            "key_stats": key_stats,
            "fpts": round(fpts, 1),
            "grade": grade,
            "type": "pitcher",
        }


# ── module-level 入口，供 main.py / app.py import 使用 ──
_client = None

def _get_client() -> YahooFantasyClient:
    global _client
    if _client is None:
        _client = YahooFantasyClient()
    return _client

def get_all_teams_stats(league_id: str = None, date: str = "yesterday") -> Optional[list]:
    return _get_client().get_all_teams_stats(league_id, date=date)
