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
                    player_id = player
