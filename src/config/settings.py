
class SystemSettings:
    LOG_PATH = "results/logs/agent_activity.jsonl"
    METRICS_PATH = "results/metrics/experiment_results.json"
    LOG_DIR = "results/logs"
    METRICS_DIR = "results/metrics"

class AgentSettings:
    # Sensor Agent
    NEIGHBOR_DISCOVERY_INTERVAL = 5.0

class DetectionSettings:
    # Isolation Forest
    CONTAMINATION = 0.02
    BUFFER_SIZE = 100
    RANDOM_STATE = 42
    N_ESTIMATORS = 200
    
    # River (Half-Space Trees)
    HST_HEIGHT = 15
    HST_WINDOW_SIZE = 250
    HST_LIMITS = (0.0, 100.0) # Estimated range of data
    
    # Statistical (if used)
    Z_SCORE_THRESHOLD = 3.0
    
    # Continuous Learning
    RETRAIN_INTERVAL = 50 # Steps between retraining
    WINDOW_SIZE = 100 # Sliding window size

class CoordinationSettings:
    # Voting
    VOTE_TIMEOUT = 10.0
    ANOMALY_WINDOW_SECONDS = 3.0 # Window to agree on an anomaly
    
    # Heartbeat
    HEARTBEAT_INTERVAL = 2.0
    HEARTBEAT_TIMEOUT = 10.0 # prune after 10s of silence
    
    # Trust System
    INITIAL_TRUST = 0.5
    TRUST_REWARD = 0.05
    TRUST_PENALTY = 0.03
    MIN_TRUST_THRESHOLD = 0.0 # Floor
    MAX_TRUST_THRESHOLD = 1.0 # Ceiling
    SEVER_CONNECTION_THRESHOLD = 0.2
    CONFIRMATION_THRESHOLD = 0.4 # Minimum trust to accept a confirmation

class DataSettings:
    # Generator
    BASE_VALUE = 50.0
    NOISE_LEVEL = 0.5
    INJECTION_INTERVAL = 30.0
    INJECTION_MAGNITUDE = 100.0

# Aggregated Access
class Settings:
    SYSTEM = SystemSettings
    AGENT = AgentSettings
    DETECTION = DetectionSettings
    COORDINATION = CoordinationSettings
    DATA = DataSettings
