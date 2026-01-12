import logging
import time
from spade.agent import Agent

class BaseAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.agent_id = jid.split("@")[0]
        self.setup_logging()

    def setup_logging(self):
        self.logger = logging.getLogger(f"Agent-{self.agent_id}")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    async def setup(self):
        self.logger.info("Agent starting...")

    def on_stop(self):
        self.logger.info("Agent stopping...")
