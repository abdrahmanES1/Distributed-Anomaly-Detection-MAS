import logging
from river import anomaly
from river import compose
from river import preprocessing

class MLDetector:
    def __init__(self):

        # We use a 2-step pipeline for online learning:
        # 1. StandardScaler: Normalizes data on the fly (so the model isn't confused by scale).
        # 2. HalfSpaceTrees: The actual anomaly detection algorithm.
        #    - Fast (O(1) update)
        #    - Handles concept drift naturally
        self.model = compose.Pipeline(
            preprocessing.StandardScaler(),
            anomaly.HalfSpaceTrees(
                n_trees=10,      # Keep it lightweight
                height=6,        # Max depth for trees
                window_size=250, # How much history to remember
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
        
        # 1. Score: How weird is this new point?
        score = self.model.score_one(record)
        
        # 2. Learn: Teach the model with this new point
        self.model.learn_one(record)
        
        self.counter += 1
        
        # Give the model some time to learn before raising alarms
        if self.counter < self.learning_period:
            return False, 0.0
            
        self.is_trained = True
        
        # HST score is 0.0 to 1.0.
        is_anomaly = score > 0.7
        
        return is_anomaly, score