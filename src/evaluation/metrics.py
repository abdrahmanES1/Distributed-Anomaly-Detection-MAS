import json
import pandas as pd
from typing import List, Dict

class MetricCollector:
    def __init__(self, log_path="results/logs/agent_activity.jsonl"):
        self.log_path = log_path
        self.logs = []
        
    def load_logs(self):
        """Reads the JSONL log file."""
        self.logs = []
        try:
            with open(self.log_path, 'r') as f:
                for line in f:
                    if line.strip():
                        self.logs.append(json.loads(line))
        except FileNotFoundError:
            print(f"Log file not found: {self.log_path}")

    def calculate_metrics(self) -> Dict:
        """
        Calculates Precision, Recall, F1, and Accuracy based on log events.
        Assumptions:
        - 'injection' event marks the start of an anomaly window (e.g., 5 seconds).
        - 'detection' event inside that window is TP.
        - 'detection' event outside is FP.
        """
        injection_events = [l for l in self.logs if l.get('event_type') == 'injection']
        # Use CONSENSUS events for system-level metrics
        detection_events = [l for l in self.logs if l.get('event_type') == 'consensus_reached']
        
        # Define anomaly windows (timestamp, timestamp + 5s)
        # We assume simulation time roughly maps to log time for this prototype
        #Ideally we would use simulation step, but timestamp is what we have in logs.
        
        # For a more robust metric in this simulation, we can count events.
        # This is a simplified logic for the prototype:
        
        tp = 0
        fp = 0
        fn = 0
        
        # Simple clustering: If an injection happens, we expect detections close to it.
        # We iterate through injections
        matched_detections = set()
        
        for inj in injection_events:
            inj_time = pd.to_datetime(inj['timestamp'])
            # Look for ANY detection within 5 seconds after injection
            found_match = False
            for det in detection_events:
                det_time = pd.to_datetime(det['timestamp'])
                delta = (det_time - inj_time).total_seconds()
                
                if 0 <= delta <= 10: # 10s window to allow for propagation
                    found_match = True
                    # If this detection hasn't been counted as a TP yet
                    if str(det) not in matched_detections:
                        tp += 1
                        matched_detections.add(str(det))
            
            if not found_match:
                fn += 1 # We missed this injection
                
        # Any detection NOT matched to an injection is a FP
        for det in detection_events:
             if str(det) not in matched_detections:
                 fp += 1
                 
        # Metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Communication Cost
        total_messages = len([l for l in self.logs if 'voting' in l.get('event_type', '')])
        
        return {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": float(f"{precision:.4f}"),
            "recall": float(f"{recall:.4f}"),
            "f1_score": float(f"{f1:.4f}"),
            "communication_messages": total_messages
        }

    def generate_report(self):
        self.load_logs()
        metrics = self.calculate_metrics()
        
        print("\n" + "="*40)
        print("   🔍 FINAL EVALUATION REPORT   ")
        print("="*40)
        print(f"True Positives  : {metrics['true_positives']}")
        print(f"False Positives : {metrics['false_positives']}")
        print(f"False Negatives : {metrics['false_negatives']}")
        print("-" * 20)
        print(f"PRECISION       : {metrics['precision']}")
        print(f"RECALL          : {metrics['recall']}")
        print(f"F1 SCORE        : {metrics['f1_score']}")
        print("-" * 20)
        print(f"Total Messages  : {metrics['communication_messages']}")
        print("="*40 + "\n")
        
        # Save to file
        import os
        os.makedirs("results/metrics", exist_ok=True)
        with open("results/metrics/experiment_results.json", "w") as f:
            json.dump(metrics, f, indent=4)
