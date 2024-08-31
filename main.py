import threading
import eventlet
from flask_socketio import SocketIO, emit
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from flask_cors import CORS
from flask import Flask
from datetime import datetime
from dateutil import tz
import asyncio
import config as GLOBAL
import spade
import json
import http.client

app = Flask(__name__)
live_games = []
CORS(app)

headers = {
    'x-rapidapi-key': "c726704363mshb871d9695f7aba0p14e03fjsn9152fc2aeb7c",
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
}

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
exit_event = threading.Event()

from_zone = tz.tzutc()
to_zone = tz.tzlocal()
current_year = str(datetime.now().year)


def UTCToLocalDateTime(originalUTC):
    utc = datetime.strptime(
        originalUTC.split("+")[0], '%Y-%m-%dT%H:%M:%S')
    utc = utc.replace(tzinfo=from_zone)
    local_date_raw = str(utc.astimezone(to_zone))
    local_date = local_date_raw.split(" ")[0].replace("-", "/")

    if (local_date.split("/")[0] == current_year):
        local_date = local_date[-5:]
        local_date = local_date.split(
            "/")[1] + "/" + local_date.split("/")[0]
    else:
        local_date = local_date.split(
            "/")[2] + "/" + local_date.split("/")[1] + "/" + local_date.split("/")[0]
    local_time = local_date_raw.split("+")[0].split(" ")[1][:-3]

    return local_date, local_time


class Competitions_Agent(Agent):
    async def setup(self):
        self.fetch_behaviour = self.Fetch_Behaviour()
        self.add_behaviour(self.fetch_behaviour)

    class Fetch_Behaviour(OneShotBehaviour):
        async def on_start(self):
            print("Competitions_Agent: Starting Fetch_Behaviour. . .")

        async def run(self):
            with open('Leagues_data') as f:
                GLOBAL.leagues = json.load(f)

            emit("competitions", GLOBAL.leagues)

    async def on_end(self):
        print("Competitions_Agent: Finishing Fetch_Behaviour. . .")
        await self.stop()


class Competitions_Agent(Agent):
    async def setup(self):
        self.fetch_behaviour = self.Fetch_Behaviour()
        self.add_behaviour(self.fetch_behaviour)

    class Fetch_Behaviour(OneShotBehaviour):
        async def on_start(self):
            print("Competitions_Agent: Starting Fetch_Behaviour. . .")

        async def run(self):
            with open('Leagues_data') as f:
                GLOBAL.leagues = json.load(f)

            emit("competitions", GLOBAL.leagues)

    async def on_end(self):
        print("Competitions_Agent: Finishing Fetch_Behaviour. . .")
        await self.stop()


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
            conn.request("GET", "/v3/fixtures?live=all", headers=headers)

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
            socketio.emit("live_games", GLOBAL.live_games)

        async def on_end(self):
            print("Live_Games_Agent: Finishing Fetch_Behaviour...")
            await self.agent.stop()


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
            conn.request("GET", url, headers=headers)

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
                         str(GLOBAL.player_id), headers=headers)

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


class Get_Player_Info_Agent(Agent):
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
                         str(GLOBAL.player_season), headers=headers)

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


class Get_Player_Detailed_Info_Agent(Agent):
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
                         str(GLOBAL.player_season), headers=headers)

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


class Get_Betting_Info_Agent(Agent):
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
                         str(GLOBAL.match_ID), headers=headers)

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


class Get_Fixture_Info_Agent(Agent):
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
                         str(GLOBAL.match_ID), headers=headers)

            res = conn.getresponse()
            string = res.read().decode('utf-8')
            data = json.loads(string)

            item = data["response"][0]

            local_date, local_time = UTCToLocalDateTime(
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


class Get_Standings_Agent(Agent):
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
                             "&season=" + str(GLOBAL.season), headers=headers)

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


class Get_Match_History_Agent(Agent):
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
                         GLOBAL.team_ID + "&last=20", headers=headers)

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

                local_date, local_time = UTCToLocalDateTime(
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


class Get_Match_Future_Agent(Agent):
    async def setup(self):
        self.fetch_behaviour = self.Fetch_Behaviour()
        self.add_behaviour(self.fetch_behaviour)

    class Fetch_Behaviour(OneShotBehaviour):
        async def on_start(self):
            print("Get_Match_Future_Agent: Starting Fetch_Behaviour. . .")

        async def run(self):
            conn = http.client.HTTPSConnection(
                "api-football-v1.p.rapidapi.com")
            conn.request("GET", "/v3/fixtures?team=" +
                         GLOBAL.team_ID + "&next=10", headers=headers)

            res = conn.getresponse()
            string = res.read().decode('utf-8')
            data = json.loads(string)
            previous_game_competition = None

            GLOBAL.match_future_response.clear()

            for item in data["response"]:
                if previous_game_competition != item["league"]["name"]:
                    previous_game_competition = item["league"]["name"]
                else:
                    item["league"]["name"] = "Same"

                local_date, local_time = UTCToLocalDateTime(
                    item["fixture"]["date"])

                GLOBAL.match_future_response.append({
                    'id': item["fixture"]["id"], 'country': item["league"]["country"],
                    'countryFlag': item["league"]["flag"], 'competition': item["league"]["name"],
                    'homeTeam': item["teams"]["home"]["name"], 'homeTeamLogo': item["teams"]["home"]["logo"],
                    'awayTeam': item["teams"]["away"]["name"], 'awayTeamLogo': item["teams"]["away"]["logo"],
                    'goalsHome': item["goals"]["home"], 'goalsAway': item["goals"]["away"],
                    'date': local_date, 'time': local_time
                })

            emit("get_match_future", GLOBAL.match_future_response)

    async def on_end(self):
        print("Get_Match_Future_Agent: Finishing Fetch_Behaviour. . .")
        await self.stop()


class Get_Team_Info_Agent(Agent):
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
                         GLOBAL.team_ID, headers=headers)

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


@socketio.on('competitions')
def handle_competitions(msg):
    async def start_agent():
        competitions_agent = Competitions_Agent(
            "Competitions_Agent@localhost", "secret")
        await competitions_agent.start()
        await competitions_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


def live_games_refresher():
    while not exit_event.is_set():
        if GLOBAL.live_games_initial_emit:
            GLOBAL.live_games_initial_emit = False
        else:
            for _ in range(100):
                eventlet.sleep(0.1)
                if exit_event.is_set():
                    print("STOPPING LIVE GAMES AGENT")
                    return

        with app.test_request_context():
            async def start_agent_thread():
                live_games_agent = Live_Games_Agent(
                    "Live_Games_Agent@localhost", "secret")
                await live_games_agent.start()
                await live_games_agent.fetch_behaviour.join()
            asyncio.run(start_agent_thread())
    print("STOPPING LIVE GAMES AGENT")


@socketio.on('live_games')
def handle_live_games(msg):
    print("Received: ", msg)
    GLOBAL.live_active = msg
    GLOBAL.live_games_initial_emit = True
    if msg:
        exit_event.clear()  # False
        print("STARTING LIVE GAMES AGENT")
        thread = socketio.start_background_task(target=live_games_refresher)
        thread.join()
    else:
        exit_event.set()  # True


@socketio.on('search_player')
def handle_search_player(msg):
    async def start_agent():
        GLOBAL.input_value = msg
        search_player_agent = Search_Player_Agent(
            "Search_Player_Agent@localhost", "secret")
        await search_player_agent.start()
        await search_player_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@socketio.on('search_player_seasons')
def handle_search_player_seasons(msg):
    async def start_agent():
        GLOBAL.player_id = msg
        search_player_seasons_agent = Search_Player_Seasons_Agent(
            "Search_Player_Seasons_Agent@localhost", "secret")
        await search_player_seasons_agent.start()
        await search_player_seasons_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@socketio.on('get_player_info')
def handle_get_player_info(msg):
    async def start_agent():
        GLOBAL.player_id = msg[0]
        GLOBAL.player_season = msg[1]
        get_player_info_agent = Get_Player_Info_Agent(
            "Get_Player_Info_Agent@localhost", "secret")
        await get_player_info_agent.start()
        await get_player_info_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@socketio.on('get_player_detailed_info')
def handle_get_player_detailed_info(msg):
    async def start_agent():
        GLOBAL.player_season = msg
        get_player_detailed_info_agent = Get_Player_Detailed_Info_Agent(
            "Get_Player_Detailed_Info_Agent@localhost", "secret")
        await get_player_detailed_info_agent.start()
        await get_player_detailed_info_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@socketio.on('get_fixture_info')
def handle_get_fixture_info(msg):
    async def start_agent():
        GLOBAL.match_ID = msg
        get_fixture_info_agent = Get_Fixture_Info_Agent(
            "Get_Fixture_Info_Agent@localhost", "secret")
        await get_fixture_info_agent.start()
        await get_fixture_info_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@socketio.on('get_betting_info')
def handle_get_betting_info(msg):
    async def start_agent():
        GLOBAL.match_ID = msg
        get_betting_info_agent = Get_Betting_Info_Agent(
            "Get_Betting_Info_Agent@localhost", "secret")
        await get_betting_info_agent.start()
        await get_betting_info_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@socketio.on('get_standings')
def handle_get_standings(msg):
    async def start_agent():
        GLOBAL.league_ID, GLOBAL.season = msg[0], msg[1]
        get_standing_agent = Get_Standings_Agent(
            "Get_Standings_Agent@localhost", "secret")
        await get_standing_agent.start()
        await get_standing_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@socketio.on('get_match_history')
def handle_get_match_history(msg):
    async def start_agent():
        GLOBAL.team_ID = msg
        get_match_history_agent = Get_Match_History_Agent(
            "Get_Match_History_Agent@localhost", "secret")
        await get_match_history_agent.start()
        await get_match_history_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@socketio.on('get_team_info')
def handle_get_team_info(msg):
    async def start_agent():
        GLOBAL.team_ID = msg
        get_team_info_agent = Get_Team_Info_Agent(
            "Get_Team_Info_Agent@localhost", "secret")
        await get_team_info_agent.start()
        await get_team_info_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@socketio.on('get_match_future')
def handle_get_match_future(msg):
    async def start_agent():
        GLOBAL.team_ID = msg
        get_match_future_agent = Get_Match_Future_Agent(
            "Get_Match_Future_Agent@localhost", "secret")
        await get_match_future_agent.start()
        await get_match_future_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


if __name__ == '__main__':
    socketio.run(app, debug=True, port=8080)
