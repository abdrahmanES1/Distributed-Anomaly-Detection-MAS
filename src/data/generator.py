import numpy as np
import random

class DataGenerator:
    def __init__(self, base_value=50.0, noise_level=0.5):
        self.base_value = base_value
        self.noise_level = noise_level
        self.current_step = 0
        # Random phase shift 0-2pi to decorrelate agents
        self.phase = random.uniform(0, 2 * np.pi) 

    def next(self):
        self.current_step += 1
        # Simple sine wave + noise + phase shift
        value = self.base_value + 10 * np.sin(self.current_step * 0.1 + self.phase)
        noise = np.random.normal(0, self.noise_level)
        return value + noise
        
    def inject_anomaly(self, magnitude=20.0):
        # Return a spiked value without updating internal state state permanently
        # (or depending on how we want to model it)
        return self.next() + magnitude
