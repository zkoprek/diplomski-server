from flask_socketio import emit
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
import config as GLOBAL
import json


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
