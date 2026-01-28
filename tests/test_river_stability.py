import time
import sys
import os
import random

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.detection.ml_detector import MLDetector

def test_stability():
    print("🧪 Starting River Stability & Accuracy Test...")
    detector = MLDetector()
    
    # 1. Train on Normal Data (Convergence Test)
    print("📚 Phase 1: Training on 500 normal points...")
    for i in range(500):
        # Normal data: small random noise around 10.0
        val = 10.0 + random.uniform(-0.5, 0.5)
        detector.update(val)
        
    print("✅ Training complete.")

    # 2. Accuracy Test
    print("🎯 Phase 2: Testing Accuracy (Anomaly Injection)...")
    anomaly_val = 50.0 # Clear anomaly
    is_anomaly, score = detector.update(anomaly_val)
    print(f"   Input: {anomaly_val} -> Is Anomaly: {is_anomaly} (Score: {score:.4f})")
    
    if is_anomaly:
        print("✅ SUCCESS: Detected anomaly correctly.")
    else:
        print("❌ FAILURE: Failed to detect obvious anomaly!")

    # 3. Long-Run Stability (Stress Test)
    print("🏋️ Phase 3: Stress Test (5000 points)...")
    start_time = time.time()
    
    for i in range(5000):
        val = 10.0 + random.uniform(-0.5, 0.5)
        detector.update(val)
        
    end_time = time.time()
    total_time = end_time - start_time
    avg_ms = (total_time / 5000) * 1000
    
    print(f"✅ Processed 5000 points in {total_time:.4f}s")
    print(f"⚡ Average Speed: {avg_ms:.4f} ms/point")
    
    if avg_ms < 1.0:
        print("✅ SPEED: Excellent (<1ms)")
    elif avg_ms < 10.0:
        print("✅ SPEED: Good (<10ms)")
    else:
        print("⚠️ SPEED: Slow (>10ms)")

if __name__ == "__main__":
    test_stability()
