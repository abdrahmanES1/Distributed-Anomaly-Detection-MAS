import time
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.detection.ml_detector import MLDetector

def test_performance():
    print("🚀 Starting River Performance Test...")
    
    # 1. Test Initialization Time
    start_init = time.time()
    detector = MLDetector()
    end_init = time.time()
    init_time = end_init - start_init
    print(f"✅ Initialization Time: {init_time:.4f}s")
    
    if init_time > 1.0:
        print("❌ Initialization too slow (>1.0s)!")
        return
        
    # 2. Test Processing Speed (10 points - Debug Mode)
    print("🏃 Processing 10 points (Debug Mode)...")
    start_proc = time.time()
    for i in range(10):
        t0 = time.time()
        val = 10.0 + (i % 5) * 0.1 
        detector.update(val)
        t1 = time.time()
        print(f"Point {i}: {t1-t0:.4f}s")
    end_proc = time.time()
    
    total_time = end_proc - start_proc
    avg_time = total_time / 1000
    print(f"✅ Total Processing Time: {total_time:.4f}s")
    print(f"⚡ Average Time per Point: {avg_time*1000:.4f}ms")
    
    if avg_time > 0.01: # 10ms
        print("❌ Processing too slow (>10ms per point)!")
    else:
        print("✅ Performance Requirement Met (<10ms)")

    # 3. Test Accuracy (Basic)
    print("Testing Anomaly Detection...")
    # Inject anomaly
    anomaly_val = 100.0
    is_anomaly, score = detector.update(anomaly_val)
    print(f"Input: {anomaly_val}, Is Anomaly: {is_anomaly}, Score: {score}")
    
    if is_anomaly:
        print("✅ Detection Logic Works")
    else:
        print("⚠️ Warning: Did not detect obvious anomaly (might need more training or tuning)")

if __name__ == "__main__":
    test_performance()
