from flask_socketio import emit
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
import config as GLOBAL
import json
import http.client


class Search_Player_Seasons_Agent(Agent):
    async def setup(self):
        self.fetch_behaviour = self.Fetch_Behaviour()
        self.add_behaviour(self.fetch_behaviour)

    class Fetch_Behaviour(OneShotBehaviour):
        async def on_start(self):
            print("Search_Player_Seasons_Agent: Starting Fetch_Behaviour. . .")

        async def run(self):
            conn = http.client.HTTPSConnection(
                "api-football-v1.p.rapidapi.com")
            print("Trazim sezone za: ", GLOBAL.player_id)
            conn.request("GET", "/v3/players/seasons?player=" +
                         str(GLOBAL.player_id), headers=GLOBAL.headers)

            res = conn.getresponse()
            string = res.read().decode('utf-8')
            data = json.loads(string)

            GLOBAL.player_id_seasons_response.clear()
            i = 0

            if (len(data["response"]) == 0):
                GLOBAL.player_id_seasons_response.append(0)
            else:
                for item in data["response"]:
                    GLOBAL.player_id_seasons_response.append(item)
                    i += 1

            emit("search_player_seasons", GLOBAL.player_id_seasons_response)

    async def on_end(self):
        print("Search_Player_Seasons_Agent: Finishing Fetch_Behaviour. . .")
        await self.stop()
