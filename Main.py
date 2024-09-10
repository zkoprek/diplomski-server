import eventlet
import asyncio
import config as GLOBAL
from Agents.Competitions_Agent import Competitions_Agent
from Agents.Live_Games_Agent import Live_Games_Agent
from Agents.Betting_Info_Agent import Betting_Info_Agent
from Agents.Fixture_Info_Agent import Fixture_Info_Agent
from Agents.Match_History_Agent import Match_History_Agent
from Agents.Match_Future_Agent import Match_Future_Agent
from Agents.Player_Info_Agent import Player_Info_Agent
from Agents.Player_Detailed_Info_Agent import Player_Detailed_Info_Agent
from Agents.Standings_Info_Agent import Standings_Agent
from Agents.Team_Info_Agent import Team_Info_Agent
from Agents.Search_Player_Agent import Search_Player_Agent
from Agents.Search_Player_Seasons_Agent import Search_Player_Seasons_Agent


@GLOBAL.socketio.on('competitions')
def handle_competitions(msg):
    async def start_agent():
        competitions_agent = Competitions_Agent(
            "Competitions_Agent@localhost", "secret")
        await competitions_agent.start()
        await competitions_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


def live_games_refresher():
    while not GLOBAL.exit_event.is_set():
        if GLOBAL.live_games_initial_emit:
            GLOBAL.live_games_initial_emit = False
        else:
            for _ in range(100):
                eventlet.sleep(0.1)
                if GLOBAL.exit_event.is_set():
                    print("STOPPING LIVE GAMES AGENT")
                    return

        with GLOBAL.app.test_request_context():
            async def start_agent_thread():
                live_games_agent = Live_Games_Agent(
                    "Live_Games_Agent@localhost", "secret")
                await live_games_agent.start()
                await live_games_agent.fetch_behaviour.join()
            asyncio.run(start_agent_thread())
    print("STOPPING LIVE GAMES AGENT")


@GLOBAL.socketio.on('live_games')
def handle_live_games(msg):
    print("Received: ", msg)
    GLOBAL.live_active = msg
    GLOBAL.live_games_initial_emit = True
    if msg:
        GLOBAL.exit_event.clear()  # False
        print("STARTING LIVE GAMES AGENT")
        thread = GLOBAL.socketio.start_background_task(
            target=live_games_refresher)
        thread.join()
    else:
        GLOBAL.exit_event.set()  # True


@GLOBAL.socketio.on('search_player')
def handle_search_player(msg):
    async def start_agent():
        GLOBAL.input_value = msg
        search_player_agent = Search_Player_Agent(
            "Search_Player_Agent@localhost", "secret")
        await search_player_agent.start()
        await search_player_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@GLOBAL.socketio.on('search_player_seasons')
def handle_search_player_seasons(msg):
    async def start_agent():
        GLOBAL.player_id = msg
        search_player_seasons_agent = Search_Player_Seasons_Agent(
            "Search_Player_Seasons_Agent@localhost", "secret")
        await search_player_seasons_agent.start()
        await search_player_seasons_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@GLOBAL.socketio.on('get_player_info')
def handle_get_player_info(msg):
    async def start_agent():
        GLOBAL.player_id = msg[0]
        GLOBAL.player_season = msg[1]
        get_player_info_agent = Player_Info_Agent(
            "Player_Info_Agent@localhost", "secret")
        await get_player_info_agent.start()
        await get_player_info_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@GLOBAL.socketio.on('get_player_detailed_info')
def handle_player_detailed_info(msg):
    async def start_agent():
        GLOBAL.player_season = msg
        get_player_detailed_info_agent = Player_Detailed_Info_Agent(
            "Player_Detailed_Info_Agent@localhost", "secret")
        await get_player_detailed_info_agent.start()
        await get_player_detailed_info_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@GLOBAL.socketio.on('get_fixture_info')
def handle_get_fixture_info(msg):
    async def start_agent():
        GLOBAL.match_ID = msg
        get_fixture_info_agent = Fixture_Info_Agent(
            "Fixture_Info_Agent@localhost", "secret")
        await get_fixture_info_agent.start()
        await get_fixture_info_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@GLOBAL.socketio.on('get_betting_info')
def handle_get_betting_info(msg):
    async def start_agent():
        GLOBAL.match_ID = msg
        get_betting_info_agent = Betting_Info_Agent(
            "Betting_Info_Agent@localhost", "secret")
        await get_betting_info_agent.start()
        await get_betting_info_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@GLOBAL.socketio.on('get_standings')
def handle_get_standings(msg):
    async def start_agent():
        GLOBAL.league_ID, GLOBAL.season = msg[0], msg[1]
        get_standing_agent = Standings_Agent(
            "Standings_Agent@localhost", "secret")
        await get_standing_agent.start()
        await get_standing_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@GLOBAL.socketio.on('get_match_history')
def handle_get_match_history(msg):
    async def start_agent():
        GLOBAL.team_ID = msg
        get_match_history_agent = Match_History_Agent(
            "Match_History_Agent@localhost", "secret")
        await get_match_history_agent.start()
        await get_match_history_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@GLOBAL.socketio.on('get_team_info')
def handle_get_team_info(msg):
    async def start_agent():
        GLOBAL.team_ID = msg
        get_team_info_agent = Team_Info_Agent(
            "Team_Info_Agent@localhost", "secret")
        await get_team_info_agent.start()
        await get_team_info_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


@GLOBAL.socketio.on('get_match_future')
def handle_get_match_future(msg):
    async def start_agent():
        GLOBAL.team_ID = msg
        get_match_future_agent = Match_Future_Agent(
            "Match_Future_Agent@localhost", "secret")
        await get_match_future_agent.start()
        await get_match_future_agent.fetch_behaviour.join()
    asyncio.run(start_agent())


if __name__ == '__main__':
    GLOBAL.socketio.run(GLOBAL.app, debug=True, host="0.0.0.0", port=8080)
