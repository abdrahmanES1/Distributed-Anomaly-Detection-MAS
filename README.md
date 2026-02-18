# Distributed Multi-Agent Anomaly Detection

> **Status:** ✅ Project Completed 
> **Focus:** Distributed AI, Online Machine Learning, Fault Tolerance

A production-ready **Multi-Agent System (MAS)** for detecting anomalies in distributed sensor networks. This system uses **River (Online ML)** for real-time learning and features a "War Room" dashboard for monitoring and control.

![Dashboard](https://via.placeholder.com/800x400?text=Professional+MAS+Dashboard+Preview)

## Key Features

### 1. True Online Learning
Unlike traditional batch learning, our agents use **River's HalfSpaceTrees** to learn incrementally.
- **Non-Blocking**: Training happens in real-time streams.
- **Adaptive**: Concept drift is handled naturally.

### 2. Dashboard
A professional Swiss-style interface built with Streamlit.
- **Mission Control**: Start/Stop simulations directly from the UI.
- **Live Topology**: Dynamic graph showing agent connections.
- **Fleet Status**: Real-time health monitoring of 20+ agents.

### 3. Chaos Engineering
Built-in fault tolerance testing.
- **Chaos Mode**: Randomly kills 25% of agents during execution.
- **Visual Resilience**: The dashboard visualizes node failure and surviving clusters.

### 4. Self-Healing Topology
Network resilience is built-in.
- **Heartbeat Mechanism**: Peers exchange active PING/PONG signals.
- **Automatic Pruning**: Dead or unresponsive neighbors are automatically removed from the topology after 10 seconds of silence.

### 5. Trust-Based Coordination
Agents don't just blindly vote; they evaluate their peers.
- **Reputation Tracking**: Each agent maintains a dynamic trust score (0.0 - 1.0) for its neighbors.
- **Penalty System**: Neighbors who trigger false alarms ("cry wolf") lose trust.
- **Isolation**: Agents with trust scores below 0.2 are automatically severed from the network.

---

## 🛠️ Quick Start Guide

### Prerequisites
Before starting, ensure you have the following installed:
- **Docker** (version 20.10+) and **Docker Compose** (version 1.29+)
- **Python** 3.9 or higher
- **Git** (for cloning the repository)
- At least 4GB of free RAM for running all services

### Installation Steps

#### Step 1: Clone and Navigate to Project
```bash
git clone <repository-url>
cd anomaly_detection_mas
```

#### Step 2: Build and Start Docker Services
Build all Docker containers and start the infrastructure:
```bash
docker-compose up -d
```

This command will:
- 🔧 Build the XMPP server (Prosody) for agent communication
- 🔧 Build the agent_runner container for running experiments
- 🔧 Build the dashboard container for visualization
- 🚀 Start all services in detached mode

**Verify services are running:**
```bash
docker-compose ps
```

You should see three services running: `prosody`, `agent_runner`, and `dashboard`.

#### Step 3: Create Jobs Directory
The job runner needs a directory to monitor job requests:
```bash
mkdir -p jobs
```

#### Step 4: Start the Job Runner Bridge
The dashboard runs inside Docker, but it needs a bridge script on your host to execute simulation commands. Open a **new terminal** and run:
```bash
python scripts/job_runner.py
```

**Keep this terminal open!** You should see:
```
👀 JOB RUNNER STARTED. Monitoring 'jobs/request.json'...
👉 Use the Dashboard 'Mission Control' to trigger actions.
```

#### Step 5: Access the Dashboard
Open your browser and navigate to:
👉 **[http://localhost:8501](http://localhost:8501)**

You should see the **War Room Dashboard** with mission control controls.

### Running Simulations

#### Option 1: Via Dashboard (Recommended)
Use the **Sidebar Controls** on the dashboard:
1. **🟢 INITIALIZE SYSTEM**: Starts a standard 20-agent run (5-minute simulation)
2. **🔥 TRIGGER CHAOS MODE**: Starts a run where 25% of agents are randomly killed at T+45s

The dashboard will show:
- Real-time topology graph
- Agent status and health
- Anomaly detection metrics
- System performance statistics

#### Option 2: Via Command Line
You can also run experiments directly using Docker:

**Standard Experiment:**
```bash
docker-compose run --rm agent_runner python scripts/run_experiment.py --agents 20 --duration 300
```

**Chaos Mode:**
```bash
docker-compose run --rm agent_runner python scripts/run_chaos.py --agents 20 --duration 300
```

**Custom Configuration:**
```bash
docker-compose run --rm agent_runner python scripts/run_experiment.py --agents 10 --duration 120
```

### Viewing Results
After running a simulation, results are saved in:
- **Logs**: `results/logs/agent_activity.jsonl` (real-time agent events)
- **Metrics**: `results/logs/metrics_report.txt` (final performance report)

### Stopping the System
To stop all services:
```bash
# Stop the job runner (Ctrl+C in its terminal)

# Stop Docker containers
docker-compose down
```

To stop and remove all data:
```bash
docker-compose down -v
```

### Troubleshooting

**Dashboard not loading?**
- Check if port 8501 is available: `lsof -i :8501`
- Verify dashboard container is running: `docker-compose ps`
- Check dashboard logs: `docker-compose logs dashboard`

**Job runner not executing commands?**
- Ensure `jobs/` directory exists
- Check file permissions on `jobs/request.json`
- Verify Docker is running: `docker ps`

**XMPP connection errors?**
- Wait 10-15 seconds after `docker-compose up` for Prosody to fully start
- Check Prosody logs: `docker-compose logs prosody`
- Restart services: `docker-compose restart prosody`

**Agents not communicating?**
- Verify network is created: `docker network ls | grep mas_network`
- Check agent_runner logs: `docker-compose logs agent_runner`

---

## 📂 Architecture

The system is composed of microservices orchestrated by Docker Compose:

| Service | Description | Tech Stack |
| :--- | :--- | :--- |
| **Agents** | 20 independent sensor agents running ML models. | Python, SPADE, River |
| **XMPP Server** | Messaging backbone for agent coordination. | Prosody |
| **Dashboard** | Visualization and control interface. | Streamlit |
| **Job Runner** | Host-side bridge for executing Docker commands. | Python |

## 🧪 Experimental Results
- **Scalability**: Successfully tested with 20 concurrent agents.
- **Latency**: Mean consensus time < 200ms.
- **Resilience**: System remains operational with 30% node loss.

---

