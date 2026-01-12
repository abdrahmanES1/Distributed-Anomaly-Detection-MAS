import numpy as np
from sklearn.ensemble import IsolationForest

class MLDetector:
    def __init__(self, contamination=0.1):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.training_data = []
        self.is_trained = False
        self.buffer_size = 50 # Number of points to collect before training

    def update(self, value):
        # normalize value to 2D array for sklearn
        point = np.array([[value]])
        
        if not self.is_trained:
            self.training_data.append(value)
            if len(self.training_data) >= self.buffer_size:
                self.train()
            return False, 0.0
        
        # Predict: 1 for inlier, -1 for outlier
        prediction = self.model.predict(point)[0]
        score = self.model.decision_function(point)[0]
        
        is_anomaly = prediction == -1
        return is_anomaly, score

    def train(self):
        print("Training Isolation Forest model...")
        X = np.array(self.training_data).reshape(-1, 1)
        self.model.fit(X)
        self.is_trained = True
        print(f"Model trained on {len(self.training_data)} points.")
