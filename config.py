import threading
from flask_socketio import SocketIO
from flask_cors import CORS
from flask import Flask
from datetime import datetime
from dateutil import tz
import config as GLOBAL

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
    utc = utc.replace(tzinfo=GLOBAL.from_zone)
    local_date_raw = str(utc.astimezone(GLOBAL.to_zone))
    local_date = local_date_raw.split(" ")[0].replace("-", "/")

    if (local_date.split("/")[0] == GLOBAL.current_year):
        local_date = local_date[-5:]
        local_date = local_date.split(
            "/")[1] + "/" + local_date.split("/")[0]
    else:
        local_date = local_date.split(
            "/")[2] + "/" + local_date.split("/")[1] + "/" + local_date.split("/")[0]
    local_time = local_date_raw.split("+")[0].split(" ")[1][:-3]

    return local_date, local_time


live_games_initial_emit = True

leagues = []
live_active = False
live_games = []
search_player = []
input_value = ""
input_response = []
player_id = None
player_id_seasons_response = []
get_player_info_response = None
get_player_detailed_info_response = []
player_season = None
match_ID = None
betting_info_response = []
fixture_info_response = None

homeCoef = None
drawCoef = None
awayCoef = None

league_ID = None
season = None

standings_response = None

team_ID = None
match_history_response = []
team_info_team_response = None
team_info_venue_response = None
match_future_response = []

originalUTC = None
local_date = None
local_time = None
