import asyncio
import time
from spade.behaviour import CyclicBehaviour
from src.data.generator import DataGenerator
from src.detection.ml_detector import MLDetector

class MonitoringBehavior(CyclicBehaviour):
    async def on_start(self):
        self.generator = DataGenerator()
        self.detector = MLDetector()
        print(f"[{self.agent.agent_id}] Monitoring started. Gathering training data...")

    async def run(self):
        # Generate data
        if self.generator.current_step == 80: # Inject later to allow training
            data_point = self.generator.inject_anomaly(magnitude=100.0)
            print(f"[{self.agent.agent_id}] 💉 INJECTING ANOMALY: {data_point:.2f}")
        else:
            data_point = self.generator.next()
        
        # Detect
        self.is_anomaly, self.z_score = self.detector.update(data_point)
        
        if not self.detector.is_trained:
             # Still training, just log occasionally
             if self.generator.current_step % 10 == 0:
                 print(f"[{self.agent.agent_id}] Training... ({len(self.detector.training_data)}/{self.detector.buffer_size})")
        
        elif self.is_anomaly:
            self.last_anomaly_time = time.time()
            print(f"[{self.agent.agent_id}] 🚨 ML ANOMALY DETECTED! Value: {data_point:.2f}, Score: {self.z_score:.2f}")
            # Trigger coordination
            if hasattr(self.agent, 'coordination'):
                 await self.agent.coordination.start_voting()
        else:
            # print(f"[{self.agent.agent_id}] Normal: {data_point:.2f}")
            pass
            
        await asyncio.sleep(0.1)
