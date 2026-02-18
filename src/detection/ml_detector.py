import logging
from river import anomaly
from river import compose
from river import preprocessing

class MLDetector:
    def __init__(self):
        # 3-Stage Pipeline:
        # 1. StandardScaler: Normalizes data (Z-score) online so trees work on stable range.
        # 2. HalfSpaceTrees: The actual anomaly detection forest.
        # Tuned parameters:
        # - n_trees: 10 (Lightweight)
        # - height: 6 (Prevent recursion)
        # - window_size: 250
        self.model = compose.Pipeline(
            preprocessing.StandardScaler(),
            anomaly.HalfSpaceTrees(
                n_trees=10,
                height=6,
                window_size=250,
                seed=42
            )
        )
        self.learning_period = 50 
        self.counter = 0
        self.is_trained = False

    def update(self, value):
        """
        Update the model with a new value and return likely anomaly status.
        Args:
            value (float): The new data point.
        Returns:
            tuple: (is_anomaly (bool), score (float))
        """
        # Pipeline expects dictionary
        record = {'val': value}
        
        # 1. Score (Pipeline propagates dict -> Scaler -> HST)
        score = self.model.score_one(record)
        
        # 2. Learn
        self.model.learn_one(record)
        
        self.counter += 1
        
        # Warm-up period
        if self.counter < self.learning_period:
            return False, 0.0
            
        self.is_trained = True
        
        # HST score is 0.0 to 1.0.
        is_anomaly = score > 0.7
        
        return is_anomaly, score