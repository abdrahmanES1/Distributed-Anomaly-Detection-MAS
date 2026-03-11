# Distributed Multi-Agent Anomaly Detection

**Project Status:** Active
**Technical Focus:** Distributed Artificial Intelligence, Online Machine Learning, and Fault-Tolerant Systems

A production-ready Multi-Agent System (MAS) for detecting anomalies in distributed sensor networks. This system leverages River (Online Machine Learning) for real-time learning and features a "War Room" dashboard for monitoring and control.

![Dashboard](https://via.placeholder.com/800x400?text=Professional+MAS+Dashboard+Preview)

## Key Technical Features

### 1. Online Machine Learning Integration
The system utilizes River's HalfSpaceTrees for incremental learning, representing a shift from traditional batch learning to streaming intelligence.
- **Non-Blocking Execution**: Model training occurs within real-time data streams.
- **Adaptive Learning**: Naturally accommodates concept drift in sensor data.

### 2. Monitoring Dashboard
A sophisticated Streamlit-based interface designed for centralized visibility and control.
- **Mission Control**: Direct initiation and termination of simulations.
- **Dynamic Topology**: Real-time graph visualization of agent interconnections.
- **Fleet Analytics**: Health monitoring for 20+ agents simultaneously.

### 3. Resilience and Chaos Engineering
The architecture includes built-in mechanisms for fault tolerance testing.
- **Chaos Mode**: Automated testing by simulating random agent failures across the network.
- **Visual Resilience**: Real-time visualization of network health and surviving clusters during failure scenarios.

### 4. Self-Healing Network Topology
Resilience is integrated into the core communication layer.
- **Liveness Monitoring**: Peers exchange periodic heartbeat signals.
- **Automated Pruning**: Unresponsive nodes are automatically identified and removed from the active topology.

### 5. Trust-Based Peer Coordination
Agents evaluate peer performance to ensure reliable detection.
- **Reputation Metrics**: Dynamic trust score maintenance for neighboring agents.
- **Consensus Logic**: Collaborative validation of anomalies to reduce false positives.
- **Automated Isolation**: Systems with consistently low trust scores are isolated from the network.

---

## Technical Setup Guide

### System Requirements
Before initialization, ensure the following are installed:
- Docker (v20.10+) and Docker Compose
- Python 3.9+
- Git
- Recommended RAM: 4GB+

### Installation

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd anomaly_detection_mas
```

#### 2. Initialize Infrastructure
Build and start the microservices using Docker Compose:
```bash
docker-compose up -d
```

This process initializes:
- Prosody (XMPP messaging backbone)
- Agent Runner (Experiment execution environment)
- Dashboard (Visualization suite)

**Verify Service Health:**
```bash
docker-compose ps
```

#### 3. Configure Workspace
```bash
mkdir -p jobs
```

#### 4. Initialize Job Runner Bridge
The dashboard requires a host-side bridge for command execution. Run the following in a dedicated terminal:
```bash
python scripts/job_runner.py
```

#### 5. Access the Dashboard
Navigate to: [http://localhost:8501](http://localhost:8501)

---

## Operating Simulations

### Via Dashboard
The sidebar provides primary controls:
- **Initialize System**: Standard 20-agent simulation.
- **Trigger Chaos Mode**: Simulation with randomized agent failures.

### Via Command Line
Direct execution via Docker:

**Standard Run:**
```bash
docker-compose run --rm agent_runner python scripts/run_experiment.py --agents 20 --duration 300
```

**Chaos Run:**
```bash
docker-compose run --rm agent_runner python scripts/run_chaos.py --agents 20 --duration 300
```

---

## System Architecture

The platform utilizes a microservices architecture orchestrated by Docker:

| Component | Responsibility | Technical Stack |
| :--- | :--- | :--- |
| **Agents** | Independent sensor nodes with embedded ML. | Python, SPADE, River |
| **Communication** | Secure, asynchronous messaging backbone. | XMPP (Prosody) |
| **Observation** | Real-time visualization and analytics. | Streamlit |
| **Bridging** | Secure host-to-container command relay. | Python |

## Performance Benchmarks
- **Scalability**: Validated for 20+ concurrent agents.
- **Consensus Latency**: Mean time to agreement under 200ms.
- **Network Resilience**: Full operational integrity maintained despite 30% node loss.

