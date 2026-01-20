import numpy as np
from river import anomaly
from src.config.settings import Settings

class MLDetector:
    """
    Streaming Anomaly Detector using Half-Space Trees (River library).
    
    This detector learns incrementally from the data stream and does not require
    periodic retraining or window buffering, making it O(1) in time and memory.
    """
    
    def __init__(self):
        """Initializes the Half-Space Trees model with configured parameters."""
        self.model = anomaly.HalfSpaceTrees(
            n_trees=Settings.DETECTION.N_ESTIMATORS,
            height=Settings.DETECTION.HST_HEIGHT,
            window_size=Settings.DETECTION.HST_WINDOW_SIZE,
            limits={0: Settings.DETECTION.HST_LIMITS}, # Feature 0 range
            seed=Settings.DETECTION.RANDOM_STATE
        )
        self.is_trained = True # Online models are always "training"
        self.step_counter = 0

    def update(self, value: float) -> tuple[bool, float]:
        """
        Updates the model with a new data point and returns the anomaly status.
        
        Args:
            value (float): The new data point to process.
            
        Returns:
            tuple[bool, float]: A tuple containing:
                - is_anomaly (bool): True if the point is anomalous.
                - score (float): The anomaly score (0 to 1).
        """
        # River expects a dict for features
        x = {0: value} 
        
        # 1. Get score (predict first)
        score = self.model.score_one(x)
        
        # 2. Update model (learn)
        self.model.learn_one(x)
        
        # 3. Determine threshold (River scores are 0.0 to 1.0, where 1.0 is high anomaly)
        # We can use a dynamic threshold or a fixed one. 
        # For HST, 0.5 - 0.8 is usually a good range. Let's map Settings.CONTAMINATION or use a new logic.
        # Since sklearn uses decision_function, we need to adapt.
        # Let's assume > 0.7 is anomaly for now, or adapt Z_SCORE settings.
        # Actually, let's use a dynamic threshold or a fixed safe one.
        # The user wants "Professional", so let's use a fixed threshold of 0.7 for now.
        
        threshold = 0.7 # TODO: Move to Settings if successful
        is_anomaly = score > threshold
        
        return is_anomaly, score

    def train(self):
        """No-op for online learning."""
        pass
