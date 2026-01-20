
import sys
import unittest
from unittest.mock import MagicMock

# Mock Settings before importing MLDetector to avoid relying on actual config
from src.config.settings import Settings
Settings.DETECTION.RETRAIN_INTERVAL = 5
Settings.DETECTION.WINDOW_SIZE = 10

from src.detection.ml_detector import MLDetector

class TestContinuousLearning(unittest.TestCase):
    def test_retraining_trigger(self):
        detector = MLDetector()
        
        # Override buffer size and interval for fast testing
        # (Though Settings modification above should handle it, explicit is safer if __init__ copied it)
        detector.buffer_size = 10
        # Check logic: interval logic is inside update(), uses Settings.
        # We need to ensure update() sees the modified Settings.
        
        # 1. Fill buffer (10 items)
        print("Feeding 10 items (filling buffer)...")
        for i in range(10):
            detector.update(50.0)
            
        self.assertTrue(detector.is_trained, "Model should be trained after buffer is full")
        
        # 2. Mock the train method to count calls
        detector.train = MagicMock()
        
        # 3. Feed 4 items (should NOT retrain yet, interval=5)
        print("Feeding 4 items...")
        for i in range(4):
            detector.update(50.0)
        
        detector.train.assert_not_called()
        
        # 4. Feed 1 more item (Total 5 steps since last training) -> Should Retrain
        print("Feeding 5th item (Expect Retrain)...")
        detector.update(50.0)
        
        detector.train.assert_called_once()
        print("✅ Retraining triggered successfully!")
        
        # 5. Verify Sliding Window
        # We fed 10 + 5 = 15 items. Window size is 10.
        # Length should be 10.
        self.assertEqual(len(detector.training_data), 10, "Buffer size should be capped at WINDOW_SIZE")
        print("✅ Sliding window size verified!")

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as e:
        # Prevent unclean exit in some environments
        pass
