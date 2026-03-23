import json
import requests

with open("oauth2.json") as f:
    creds = json.load(f)

headers = {
    "Authorization": "Bearer " + creds["access_token"],
    "Accept": "application/json",
}

# 取得所有賽季的 MLB game
url = "https://fantasysports.yahooapis.com/fantasy/v2/games;game_codes=mlb?format=json"
resp = requests.get(url, headers=headers)
data = resp.json()

# 列出所有 MLB game_key 和賽季
try:
    games = data["fantasy_content"]["games"]
    count = games["count"]
    for i in range(count):
        g = games[str(i)]["game"][0]
        print("game_key:", g.get("game_key"), "season:", g.get("season"), "is_game_over:", g.get("is_game_over"))
except Exception as e:
    print("Error:", e)
    print(resp.text[:1000])
