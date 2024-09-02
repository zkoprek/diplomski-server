from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
import config as GLOBAL
import json
import http.client


class Live_Games_Agent(Agent):
    async def setup(self):
        self.fetch_behaviour = self.Fetch_Behaviour()
        self.add_behaviour(self.fetch_behaviour)

    class Fetch_Behaviour(OneShotBehaviour):
        async def on_start(self):
            print("Live_Games_Agent: Starting Fetch_Behaviour...")

        async def run(self):
            conn = http.client.HTTPSConnection(
                "api-football-v1.p.rapidapi.com")
            conn.request("GET", "/v3/fixtures?live=all",
                         headers=GLOBAL.headers)

            res = conn.getresponse()
            string = res.read().decode('utf-8')
            data = json.loads(string)
            previous_game_competition = None

            GLOBAL.live_games = []

            for item in data["response"]:
                if previous_game_competition != item["league"]["name"]:
                    previous_game_competition = item["league"]["name"]
                else:
                    item["league"]["name"] = "Same"
                game_json = {"id": item["fixture"]["id"], "country": item["league"]["country"], "countryFlag": item["league"]["flag"], "competition": item["league"]["name"], "homeTeam": item["teams"]["home"]["name"], "homeTeamLogo": item["teams"]["home"]["logo"], "awayTeam": item["teams"]["away"]["name"], "awayTeamLogo": item["teams"]["away"]["logo"],
                             "goalsHome": item["goals"]["home"], "goalsAway": item["goals"]["away"], "statusShort": item["fixture"]["status"]["short"], "elapsed": item["fixture"]["status"]["elapsed"]}
                GLOBAL.live_games.append(game_json)

            print("Emitting live_games...")
            GLOBAL.socketio.emit("live_games", GLOBAL.live_games)

        async def on_end(self):
            print("Live_Games_Agent: Finishing Fetch_Behaviour...")
            await self.agent.stop()
