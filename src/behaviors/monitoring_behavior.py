import asyncio
import time
from spade.behaviour import CyclicBehaviour
from src.data.generator import DataGenerator
from src.detection.ml_detector import MLDetector
from src.config.settings import Settings

class MonitoringBehavior(CyclicBehaviour):
    async def on_start(self):
        self.generator = DataGenerator()
        self.detector = MLDetector()
        print(f"[{self.agent.agent_id}] Transformer online. Monitoring AC Voltage...")
        self.start_time = time.time()
        # Initialize to previous sync window so we don't immediately spike on boot
        self.last_injection_time = (time.time() // Settings.DATA.INJECTION_INTERVAL) * Settings.DATA.INJECTION_INTERVAL

    async def run(self):
        # 1. Get Data check for injection
        current_time = time.time()
        
        # Use modulo arithmetic on global time so ALL agents trigger at the exact same moment
        # creating a true "Grid-Wide Surge" that neighbors will AGREE on.
        current_window = current_time // Settings.DATA.INJECTION_INTERVAL
        last_window = self.last_injection_time // Settings.DATA.INJECTION_INTERVAL
        
        if current_window > last_window:
            # Randomly decide if this is a GLOBAL (Grid-Wide) or LOCAL anomaly
            import random
            is_global = random.random() > 0.5
            
            # If Global, everyone spikes. If Local, only 1 in 5 agents spike independently.
            if is_global or random.random() < 0.2:
                data_point = self.generator.inject_anomaly(magnitude=Settings.DATA.INJECTION_MAGNITUDE)
                event_name = "GLOBAL" if is_global else "LOCAL"
                self.agent.log_info(f"⚡ FAKE {event_name} SURGE INJECTED: {data_point:.2f}V", event_type="injection", magnitude=Settings.DATA.INJECTION_MAGNITUDE, value=data_point)
            else:
                data_point = self.generator.next()
                
            self.last_injection_time = current_time
        else:
            # Normal AC Voltage generation
            data_point = self.generator.next()
        
        # 2. Check for Anomalies
        self.is_anomaly, self.z_score = self.detector.update(data_point)
        
        if self.is_anomaly:
            self.last_anomaly_time = time.time()
            self.agent.log_info(f"🚨 VOLTAGE SURGE (Local Detection): {data_point:.2f}V", event_type="detection", value=data_point, score=self.z_score)
            
            # 3. Ask neighbors: "Is this a grid-wide surge or just my street?"
            if hasattr(self.agent, 'coordination'):
                 await self.agent.coordination.start_voting()
        else:
            pass

            
        await asyncio.sleep(0.1)
