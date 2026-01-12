import logging
from spade.agent import Agent
from src.utils.logger import setup_logger

class BaseAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.agent_id = str(jid).split("@")[0]
        # Initialize structured logger
        self.logger = setup_logger(f"Agent-{self.agent_id}", self.agent_id)

    async def setup(self):
        self.logger.info("Agent starting...")

    def log_info(self, message, **kwargs):
        """Helper to log with extra JSON data"""
        self.logger.info(message, extra={"agent_id": self.agent_id, "custom_data": kwargs})


    def on_stop(self):
        self.logger.info("Agent stopping...")
