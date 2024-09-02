from flask_socketio import emit
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
import config as GLOBAL
import json
import http.client


class Match_History_Agent(Agent):
    async def setup(self):
        self.fetch_behaviour = self.Fetch_Behaviour()
        self.add_behaviour(self.fetch_behaviour)

    class Fetch_Behaviour(OneShotBehaviour):
        async def on_start(self):
            print("Get_Match_History_Agent: Starting Fetch_Behaviour. . .")

        async def run(self):
            conn = http.client.HTTPSConnection(
                "api-football-v1.p.rapidapi.com")
            conn.request("GET", "/v3/fixtures?team=" +
                         GLOBAL.team_ID + "&last=20", headers=GLOBAL.headers)

            res = conn.getresponse()
            string = res.read().decode('utf-8')
            data = json.loads(string)
            previous_game_competition = None

            GLOBAL.match_history_response.clear()

            for item in data["response"]:
                if previous_game_competition != item["league"]["name"]:
                    previous_game_competition = item["league"]["name"]
                else:
                    item["league"]["name"] = "Same"

                local_date, local_time = GLOBAL.UTCToLocalDateTime(
                    item["fixture"]["date"])

                GLOBAL.match_history_response.append({
                    'id': item["fixture"]["id"], 'country': item["league"]["country"],
                    'countryFlag': item["league"]["flag"], 'competition': item["league"]["name"],
                    'homeTeam': item["teams"]["home"]["name"], 'homeTeamLogo': item["teams"]["home"]["logo"],
                    'awayTeam': item["teams"]["away"]["name"], 'awayTeamLogo': item["teams"]["away"]["logo"],
                    'goalsHome': item["goals"]["home"], 'goalsAway': item["goals"]["away"],
                    'date': local_date, 'time': local_time
                })

            emit("get_match_history", GLOBAL.match_history_response)

    async def on_end(self):
        print("Get_Match_History_Agent: Finishing Fetch_Behaviour. . .")
        await self.stop()
