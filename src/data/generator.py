import numpy as np
import random

class DataGenerator:
    def __init__(self, base_value=230.0, noise_level=2.0):
        # 230V represents standard European/global AC mains voltage
        self.base_value = base_value
        self.noise_level = noise_level
        self.current_step = 0
        self.phase = random.uniform(0, 2 * np.pi) 

    def next(self):
        self.current_step += 1
        # Calculate AC Voltage sine wave. Amplitude is 10% of base voltage.
        value = self.base_value + (self.base_value * 0.1) * np.sin(self.current_step * 0.1 + self.phase)
        # Add normal grid noise (appliances turning on/off)
        noise = np.random.normal(0, self.noise_level)
        return value + noise
        
    def inject_anomaly(self, magnitude=100.0):
        # Simulate a severe voltage surge/spike
        return self.next() + magnitude

