from flask_socketio import emit
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
import config as GLOBAL
import json
import http.client


class Team_Info_Agent(Agent):
    async def setup(self):
        self.fetch_behaviour = self.Fetch_Behaviour()
        self.add_behaviour(self.fetch_behaviour)

    class Fetch_Behaviour(OneShotBehaviour):
        async def on_start(self):
            print("Get_Team_Info_Agent: Starting Fetch_Behaviour. . .")

        async def run(self):
            conn = http.client.HTTPSConnection(
                "api-football-v1.p.rapidapi.com")
            conn.request("GET", "/v3/teams?id=" +
                         GLOBAL.team_ID, headers=GLOBAL.headers)

            res = conn.getresponse()
            string = res.read().decode('utf-8')
            data = json.loads(string)

            item = data["response"][0]
            GLOBAL.team_info_team_response = item["team"]
            GLOBAL.team_info_venue_response = item["venue"]

            emit("get_team_info", [
                 GLOBAL.team_info_team_response, GLOBAL.team_info_venue_response])

    async def on_end(self):
        print("Get_Team_Info_Agent: Finishing Fetch_Behaviour. . .")
        await self.stop()
