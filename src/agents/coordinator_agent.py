from src.agents.base_agent import BaseAgent
from spade.behaviour import CyclicBehaviour

class CoordinatorAgent(BaseAgent):
    class ListenBehavior(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                print(f"[Coordinator] Received: {msg.body} from {msg.sender}")

    async def setup(self):
        await super().setup()
        self.add_behaviour(self.ListenBehavior())
        self.logger.info("CoordinatorAgent setup complete.")
