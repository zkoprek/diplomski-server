from flask_socketio import emit
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
import config as GLOBAL
import json
import http.client


class Search_Player_Agent(Agent):
    async def setup(self):
        self.fetch_behaviour = self.Fetch_Behaviour()
        self.add_behaviour(self.fetch_behaviour)

    class Fetch_Behaviour(OneShotBehaviour):
        async def on_start(self):
            print("Search_Player_Agent: Starting Fetch_Behaviour. . .")

        async def run(self):
            conn = http.client.HTTPSConnection(
                "api-football-v1.p.rapidapi.com")
            url = "/v2/players/search/" + GLOBAL.input_value
            url = url.replace(" ", "%20")
            conn.request("GET", url, headers=GLOBAL.headers)

            res = conn.getresponse()
            string = res.read().decode("utf-8")
            data = json.loads(string)

            GLOBAL.input_response.clear()

            for item in data["api"]["players"]:
                if item["firstname"] and item["lastname"]:
                    player_json = {'id': item["player_id"], 'firstName': item["firstname"],
                                   'lastName': item["lastname"], 'nationality': item["nationality"]}
                    GLOBAL.input_response.append(player_json)

            emit("search_player", GLOBAL.input_response)

    async def on_end(self):
        print("Search_Player_Agent: Finishing Fetch_Behaviour. . .")
        await self.stop()
