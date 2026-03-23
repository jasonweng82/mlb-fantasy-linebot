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
    負責抓取你的 Fantasy 隊伍球員昨日成績
    """

    def __init__(self):
        # OAuth2 憑證從環境變數讀取
        oauth_data = {
            "consumer_key": os.environ["YAHOO_CONSUMER_KEY"],
            "consumer_secret": os.environ["YAHOO_CONSUMER_SECRET"],
            "token": os.environ.get("YAHOO_TOKEN", ""),
            "token_secret": os.environ.get("YAHOO_TOKEN_SECRET", ""),
        }

        # 寫入暫存檔（yahoo_oauth 需要檔案）
        with open("/tmp/oauth2.json", "w") as f:
            json.dump(oauth_data, f)

        sc = OAuth2(None, None, from_file="/tmp/oauth2.json")
        self.gm = yfa.Game(sc, "mlb")

        # 自動取得當前賽季的 League
        league_ids = self.gm.league_ids()
        if not league_ids:
            raise ValueError("找不到 Yahoo Fantasy Baseball 聯盟，請確認帳號有加入聯盟")

        league_id = os.environ.get("YAHOO_LEAGUE_ID", league_ids[0])
        self.league = self.gm.to_league(league_id)
        logger.info(f"✅ 成功連線聯盟: {league_id}")

    def get_yesterday_stats(self) -> Optional[dict]:
        """
        取得昨日所有球員成績，回傳分析結果
        """
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")
        logger.info(f"📅 查詢日期: {date_str}")

        # 取得我的隊伍
        my_team = self.league.to_team(self.league.team_key())
        roster = my_team.roster(day=yesterday)

        if not roster:
            return None

        # 抓每位球員的成績
        player_stats = []
        for player in roster:
            player_id = player["player_id"]
            name = player["name"]
            position = player.get("selected_position", "BN")

            # 跳過板凳球員
            if position == "BN":
                continue

            stats = self._get_player_stats(player_id, date_str, name, position)
            if stats:
                player_stats.append(stats)

        if not player_stats:
            return None

        # 計算整體評分
        hot_players = [p for p in player_stats if p["grade"] == "hot"]
        cold_players = [p for p in player_stats if p["grade"] == "cold"]
        normal_players = [p for p in player_stats if p["grade"] == "normal"]
        total_fpts = sum(p["fpts"] for p in player_stats)

        return {
            "date": yesterday.strftime("%Y/%m/%d"),
            "hot": sorted(hot_players, key=lambda x: x["fpts"], reverse=True),
            "cold": sorted(cold_players, key=lambda x: x["fpts"]),
            "normal": normal_players,
            "total_fpts": round(total_fpts, 1),
            "player_count": len(player_stats),
        }

    def _get_player_stats(self, player_id: str, date_str: str, name: str, position: str) -> Optional[dict]:
        """
        取得單一球員當日成績並計算 Fantasy 分數
        """
        try:
            stats = self.league.player_stats([player_id], "date", date=date_str)
            if not stats:
                return None

            raw = stats[0] if isinstance(stats, list) else stats
            stat_map = raw.get("stats", {})

            is_pitcher = position in ["SP", "RP", "P"]

            if is_pitcher:
                return self._score_pitcher(name, position, stat_map)
            else:
                return self._score_batter(name, position, stat_map)

        except Exception as e:
            logger.warning(f"⚠️ 無法取得 {name} 的成績: {e}")
            return None

    def _score_batter(self, name: str, position: str, stats: dict) -> dict:
        """野手評分"""
        ab = float(stats.get("AB", 0))
        hits = float(stats.get("H", 0))
        hr = float(stats.get("HR", 0))
        rbi = float(stats.get("RBI", 0))
        r = float(stats.get("R", 0))
        sb = float(stats.get("SB", 0))
        bb = float(stats.get("BB", 0))
        so = float(stats.get("SO", 0))

        # Fantasy 積分計算（依據常見 H2H 計分）
        fpts = (hits * 1) + (hr * 4) + (rbi * 1) + (r * 1) + (sb * 2) + (bb * 0.5) - (so * 0.5)

        avg = f"{hits/ab:.3f}" if ab > 0 else ".000"
        key_stats = f"{int(hits)}/{int(ab)}"
        if hr > 0:
            key_stats += f", {int(hr)}HR"
        if rbi > 0:
            key_stats += f", {int(rbi)}RBI"
        if sb > 0:
            key_stats += f", {int(sb)}SB"
        if bb > 0:
            key_stats += f", {int(bb)}BB"

        grade = "hot" if fpts >= 5 else ("cold" if fpts <= 0 and ab >= 3 else "normal")

        return {
            "name": name,
            "position": position,
            "key_stats": key_stats,
            "fpts": round(fpts, 1),
            "grade": grade,
            "type": "batter",
        }

    def _score_pitcher(self, name: str, position: str, stats: dict) -> dict:
        """投手評分"""
        ip = float(stats.get("IP", 0))
        er = float(stats.get("ER", 0))
        k = float(stats.get("K", 0))
        w = float(stats.get("W", 0))
        sv = float(stats.get("SV", 0))
        bb = float(stats.get("BB", 0))
        hits = float(stats.get("H", 0))

        if ip == 0:
            return None  # 沒出賽跳過

        era_today = (er / ip * 9) if ip > 0 else 0

        # Fantasy 積分計算
        fpts = (ip * 3) + (k * 1) + (w * 5) + (sv * 5) - (er * 2) - (bb * 0.5)

        key_stats = f"{ip}IP, {int(k)}K"
        if w:
            key_stats += ", W"
        if sv:
            key_stats += ", SV"
        if er > 0:
            key_stats += f", {int(er)}ER"

        grade = "hot" if fpts >= 10 else ("cold" if er >= 4 else "normal")

        return {
            "name": name,
            "position": position,
            "key_stats": key_stats,
            "fpts": round(fpts, 1),
            "grade": grade,
            "type": "pitcher",
        }
