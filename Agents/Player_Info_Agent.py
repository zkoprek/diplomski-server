from flask_socketio import emit
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
import config as GLOBAL
import json
import http.client


class Player_Info_Agent(Agent):
    async def setup(self):
        self.fetch_behaviour = self.Fetch_Behaviour()
        self.add_behaviour(self.fetch_behaviour)

    class Fetch_Behaviour(OneShotBehaviour):
        async def on_start(self):
            print("Get_Player_Info_Agent: Starting Fetch_Behaviour. . .")

        async def run(self):
            conn = http.client.HTTPSConnection(
                "api-football-v1.p.rapidapi.com")
            conn.request("GET", "/v3/players?id=" + str(GLOBAL.player_id) + "&season=" +
                         str(GLOBAL.player_season), headers=GLOBAL.headers)

            res = conn.getresponse()
            string = res.read().decode('utf-8')
            data = json.loads(string)

            try:
                itemPlayer = data["response"][0]["player"]
                GLOBAL.get_player_info_response = {'id': itemPlayer["id"], 'firstName': itemPlayer["firstname"],
                                                   'lastName': itemPlayer["lastname"], 'age': itemPlayer["age"],
                                                   'birthDate': itemPlayer["birth"]["date"], 'birthPlace': itemPlayer["birth"]["place"],
                                                   'birthCountry': itemPlayer["birth"]["country"], 'nationality': itemPlayer["nationality"],
                                                   'height': itemPlayer["height"], 'weight': itemPlayer["weight"],
                                                   'injured': itemPlayer["injured"], 'photo': itemPlayer["photo"]}
            except IndexError:
                GLOBAL.get_player_info_response = {'id': "N/A", 'firstName': "N/A",
                                                   'lastName': "N/A", 'age': "N/A",
                                                   'birthDate': "N/A", 'birthPlace': "N/A",
                                                   'birthCountry': "N/A", 'nationality': "N/A",
                                                   'height': "N/A", 'weight': "N/A",
                                                   'injured': "N/A", 'photo': "N/A"}

            emit("get_player_info",
                 GLOBAL.get_player_info_response)

    async def on_end(self):
        print("Get_Player_Info_Agent: Finishing Fetch_Behaviour. . .")
        await self.stop()
