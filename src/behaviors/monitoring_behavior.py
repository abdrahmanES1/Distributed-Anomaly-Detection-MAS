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
        self.start_time = time.time()
        self.last_injection_time = self.start_time

    async def run(self):
        # Generate data
        # Periodic Time-based injection every 30s
        current_time = time.time()
        if (current_time - self.last_injection_time) > 30.0:
            data_point = self.generator.inject_anomaly(magnitude=100.0)
            self.agent.log_info(f"💉 INJECTING ANOMALY: {data_point:.2f}", event_type="injection", magnitude=100.0, value=data_point)
            self.last_injection_time = current_time
        else:
            data_point = self.generator.next()
        
        # Detect
        self.is_anomaly, self.z_score = self.detector.update(data_point)
        
        if not self.detector.is_trained:
             # Still training, just log occasionally
             if self.generator.current_step % 10 == 0:
                 self.agent.log_info(f"Warming up model... {self.detector.counter}/{self.detector.learning_period}")
        
        elif self.is_anomaly:
            self.last_anomaly_time = time.time()
            self.agent.log_info("🚨 ML ANOMALY DETECTED!", event_type="detection", value=data_point, score=self.z_score)
            
            # Trigger coordination
            if hasattr(self.agent, 'coordination'):
                 await self.agent.coordination.start_voting()
        else:
            # self.agent.log_info(f"Normal: {data_point:.2f}")
            pass
            
        await asyncio.sleep(0.1)
