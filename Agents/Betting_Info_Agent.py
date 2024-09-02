from flask_socketio import emit
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
import config as GLOBAL
import json
import http.client


class Betting_Info_Agent(Agent):
    async def setup(self):
        self.fetch_behaviour = self.Fetch_Behaviour()
        self.add_behaviour(self.fetch_behaviour)

    class Fetch_Behaviour(OneShotBehaviour):
        async def on_start(self):
            print("Get_Betting_Info_Agent: Starting Fetch_Behaviour. . .")

        async def run(self):
            conn = http.client.HTTPSConnection(
                "api-football-v1.p.rapidapi.com")
            conn.request("GET", "/v3/odds?fixture=" +
                         str(GLOBAL.match_ID), headers=GLOBAL.headers)

            res = conn.getresponse()
            string = res.read().decode('utf-8')
            data = json.loads(string)

            GLOBAL.betting_info_response.clear()

            try:
                for item in data["response"][0]["bookmakers"]:
                    GLOBAL.betting_info_response.append({'bookmaker': item["name"], 'homeCoef': item["bets"][0]["values"][0]["odd"],
                                                        'drawCoef': item["bets"][0]["values"][1]["odd"], 'awayCoef': item["bets"][0]["values"][1]["odd"],
                                                         })
            except IndexError:
                GLOBAL.betting_info_response.append({'bookmaker': "N/A", 'homeCoef': "N/A",
                                                    'drawCoef': "N/A", 'awayCoef': "N/A",
                                                     })

            emit("get_betting_info", GLOBAL.betting_info_response)

    async def on_end(self):
        print("Get_Betting_Info_Agent: Finishing Fetch_Behaviour. . .")
        await self.stop()
