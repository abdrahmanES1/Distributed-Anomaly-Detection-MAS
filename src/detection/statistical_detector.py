import numpy as np
from collections import deque

class StatisticalDetector:
    def __init__(self, window_size=20, threshold=3.0):
        self.window_size = window_size
        self.threshold = threshold
        self.history = deque(maxlen=window_size)
    
    def update(self, value):
        self.history.append(value)
        
        if len(self.history) < self.window_size:
            return False, 0.0
        
        mean = np.mean(self.history)
        std = np.std(self.history)
        
        if std == 0:
            return False, 0.0
            
        z_score = (value - mean) / std
        is_anomaly = abs(z_score) > self.threshold
        
        return is_anomaly, z_score
