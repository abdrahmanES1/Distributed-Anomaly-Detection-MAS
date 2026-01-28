from src.agents.base_agent import BaseAgent
from src.behaviors.monitoring_behavior import MonitoringBehavior
from src.behaviors.coordination_behavior import CoordinationBehavior

class SensorAgent(BaseAgent):
    async def setup(self):
        await super().setup()
        
        # Add Monitoring Behavior
        self.monitoring = MonitoringBehavior()
        self.add_behaviour(self.monitoring)
        
        # Add Coordination Behavior
        self.coordination = CoordinationBehavior()
        self.add_behaviour(self.coordination)

        # Add Healing Behavior (Self-Repair)
        from src.behaviors.healing_behavior import HealingBehavior
        self.healing = HealingBehavior()
        self.add_behaviour(self.healing)
        
        self.log_info("SensorAgent setup complete.")

    def set_neighbors(self, neighbor_jids):
        self.neighbors = neighbor_jids
        self.log_info(f"Neighbors set: {self.neighbors}")
