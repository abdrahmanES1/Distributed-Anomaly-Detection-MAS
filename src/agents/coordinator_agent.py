from src.agents.base_agent import BaseAgent
from spade.behaviour import CyclicBehaviour

class CoordinatorAgent(BaseAgent):
    class ListenBehavior(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                self.agent.log_info(f"Received alert from {msg.sender}", event_type="alert_received", alert=msg.body)

    async def setup(self):
        await super().setup()
        self.add_behaviour(self.ListenBehavior())
        self.log_info("CoordinatorAgent setup complete.")
