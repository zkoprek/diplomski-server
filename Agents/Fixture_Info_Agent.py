from flask_socketio import emit
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
import config as GLOBAL
import json
import http.client


class Fixture_Info_Agent(Agent):
    async def setup(self):
        self.fetch_behaviour = self.Fetch_Behaviour()
        self.add_behaviour(self.fetch_behaviour)

    class Fetch_Behaviour(OneShotBehaviour):
        async def on_start(self):
            print("Get_Fixture_Info_Agent: Starting Fetch_Behaviour. . .")

        async def run(self):
            conn = http.client.HTTPSConnection(
                "api-football-v1.p.rapidapi.com")
            conn.request("GET", "/v3/fixtures?id=" +
                         str(GLOBAL.match_ID), headers=GLOBAL.headers)

            res = conn.getresponse()
            string = res.read().decode('utf-8')
            data = json.loads(string)

            item = data["response"][0]

            local_date, local_time = GLOBAL.UTCToLocalDateTime(
                item["fixture"]["date"])

            GLOBAL.fixture_info_response = {'country': item["league"]["country"], 'countryFlag': item["league"]["flag"],
                                            'competition': item["league"]["name"], 'competitionLogo': item["league"]["logo"],
                                            'homeID': str(item["teams"]["home"]["id"]), 'awayID': str(item["teams"]["away"]["id"]),
                                            'homeName': item["teams"]["home"]["name"], 'awayName': item["teams"]["away"]["name"],
                                            'homeLogo': item["teams"]["home"]["logo"], 'awayLogo': item["teams"]["away"]["logo"],
                                            'homeGoals': item["goals"]["home"], 'awayGoals': item["goals"]["away"],
                                            'elapsed': item["fixture"]["status"]["elapsed"], 'referee': item["fixture"]["referee"],
                                            'statusLong': item["fixture"]["status"]["long"], 'city': item["fixture"]["venue"]["city"],
                                            'venue': item["fixture"]["venue"]["name"], 'date': local_date, 'time': local_time
                                            }

            emit("get_fixture_info", GLOBAL.fixture_info_response)

    async def on_end(self):
        print("Get_Fixture_Info_Agent: Finishing Fetch_Behaviour. . .")
        await self.stop()
