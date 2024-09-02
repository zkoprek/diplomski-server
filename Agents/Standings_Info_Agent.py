from flask_socketio import emit
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
import config as GLOBAL
import json
import http.client


class Standings_Agent(Agent):
    async def setup(self):
        self.fetch_behaviour = self.Fetch_Behaviour()
        self.add_behaviour(self.fetch_behaviour)

    class Fetch_Behaviour(OneShotBehaviour):
        async def on_start(self):
            print("Get_Standings_Agent: Starting Fetch_Behaviour. . .")

        async def run(self):
            conn = http.client.HTTPSConnection(
                "api-football-v1.p.rapidapi.com")

            # U slučajevima nekih liga zapisi za sezonu (godinu) 2024 ne postoje, pa oni bacaju error.
            # Stoga, potrebno je dohvatiti onu podljenju koja ima zapise.
            data = None
            while not data or not data["response"]:
                conn.request("GET", "/v3/standings?league=" + GLOBAL.league_ID +
                             "&season=" + str(GLOBAL.season), headers=GLOBAL.headers)

                res = conn.getresponse()
                string = res.read().decode('utf-8')
                data = json.loads(string)
                GLOBAL.season -= 1

            r_league = data["response"][0]["league"]
            GLOBAL.standings_response = {'id': r_league["id"], 'name': r_league["name"],
                                         'country': r_league["country"], 'logo': r_league["logo"],
                                         'flag': r_league["flag"], 'season': r_league["season"],
                                         'standings': [],
                                         }

            for team in r_league["standings"][0]:
                team_json = {'id': team["team"]["id"], 'name': team["team"]["name"],
                             'rank': team["rank"], 'logo': team["team"]["logo"],
                             'points': team["points"], 'goalsDiff': team["goalsDiff"],
                             'form': [], 'description': team["description"], 'played': team["all"]["played"],
                             'win': team["all"]["win"], 'draw': team["all"]["draw"],
                             'lose': team["all"]["lose"], 'goalsFor': team["all"]["goals"]["for"],
                             'goalsAgainst': team["all"]["goals"]["against"]}

                try:
                    for x in range(0, len(team["form"])):
                        team_json["form"].append(team["form"][x])
                except TypeError:
                    pass

                GLOBAL.standings_response["standings"].append(team_json)

            emit("get_standings", GLOBAL.standings_response)

    async def on_end(self):
        print("Get_Standings_Agent: Finishing Fetch_Behaviour. . .")
        await self.stop()
