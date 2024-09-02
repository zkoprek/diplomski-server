from flask_socketio import emit
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
import config as GLOBAL
import json
import http.client


class Player_Detailed_Info_Agent(Agent):
    async def setup(self):
        self.fetch_behaviour = self.Fetch_Behaviour()
        self.add_behaviour(self.fetch_behaviour)

    class Fetch_Behaviour(OneShotBehaviour):
        async def on_start(self):
            print("Get_Player_Detailed_Info_Agent: Starting Fetch_Behaviour. . .")

        async def run(self):
            conn = http.client.HTTPSConnection(
                "api-football-v1.p.rapidapi.com")
            conn.request("GET", "/v3/players?id=" + str(GLOBAL.player_id) + "&season=" +
                         str(GLOBAL.player_season), headers=GLOBAL.headers)

            res = conn.getresponse()
            string = res.read().decode('utf-8')
            data = json.loads(string)

            GLOBAL.get_player_detailed_info_response.clear()

            for itemStat in data["response"][0]["statistics"]:
                player_detailed_json = {'teamName': itemStat["team"]["name"], 'teamLogo': itemStat["team"]["logo"],
                                        'countryName': itemStat["league"]["country"], 'countryFlag': itemStat["league"]["flag"],
                                        'leagueName': itemStat["league"]["name"], 'leagueLogo': itemStat["league"]["logo"],
                                        'appearences': itemStat["games"]["appearences"], 'lineups': itemStat["games"]["lineups"],
                                        'minutes': itemStat["games"]["minutes"], 'position': itemStat["games"]["position"],
                                        'rating': 0, 'goals': itemStat["goals"]["total"],
                                        'assists': itemStat["goals"]["assists"], 'conceded': itemStat["goals"]["conceded"],
                                        'saves': itemStat["goals"]["saves"], 'yellowCards': itemStat["cards"]["yellow"],
                                        'redCards': itemStat["cards"]["red"], 'penaltyGoals': itemStat["penalty"]["scored"]
                                        }
                if itemStat["games"]["rating"]:
                    player_detailed_json["rating"] = round(
                        (float(str(itemStat["games"]["rating"]))), 2)

                GLOBAL.get_player_detailed_info_response.append(
                    player_detailed_json)

            emit("get_player_detailed_info",
                 GLOBAL.get_player_detailed_info_response)

    async def on_end(self):
        print("Get_Player_Detailed_Info_Agent: Finishing Fetch_Behaviour. . .")
        await self.stop()
