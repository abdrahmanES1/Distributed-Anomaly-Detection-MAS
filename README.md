# Distributed Multi-Agent Anomaly Detection

> **Course:** Distributed Artificial Intelligence (SDA 2024)
> **Status:** Version 3.0 (Industrial Grade)

A robust **Distributed AI (DAI)** system for edge anomaly detection. This project implements a fully decentralized Multi-Agent System (MAS) where autonomous agents monitor local data streams, learn normal behavior using **Online Machine Learning (River Half-Space Trees)**, and coordinate via a **Meritocratic Consensus Protocol** to reach consensus on global anomalies.

## 🚀 Key Features

*   **Emergent Intelligence:** Global system state is determined solely through local peer-to-peer interactions; no central "brain" exists.
*   **O(1) Online Learning:** Replaced batch processing with **River Half-Space Trees** for constant-time, memory-efficient streaming detection.
*   **Decorrelation:** Implementation of **Phase Shift Diversity** to prevent "Echo Chamber" correlated errors among agents.
*   **Trust Modeling:** A dynamic **Meritocratic Reputation System** where agents weigh votes based on the reliability of their neighbors.
*   **Self-Healing Topology:** Agents actively monitor neighbor health via **Heartbeats** and automatically **prune dead connections** to maintain robust topology.
*   **Fully Containerized:** Built on the **SPADE** framework and **XMPP (Prosody)**, orchestrated via Docker Compose for easy deployment.

## 🛠️ Architecture

The system consists of three main components:
1.  **Sensor Agents:** The intelligent workers. They read data, run **River HST** inference, track neighbor trust, and vote.
2.  **Coordinator Agent:** An optional observer that logs finalized global alerts.
3.  **XMPP Server:** The communication backbone (Prosody) facilitating secure message passing.

### Technologies
*   **Language:** Python 3.9
*   **Framework:** SPADE (Smart Python Agent Development Environment)
*   **ML Library:** River (Online Learning)
*   **Infrastructure:** Docker & Docker Compose
*   **Protocol:** XMPP / FIPA-ACL

## 📦 Installation & Usage

### Prerequisites
*   Docker & Docker Compose installed on your machine.

### Running the Experiment

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Start-Core/anomaly_detection_mas.git
    cd anomaly_detection_mas
    ```

2.  **Start the System:**
    Run the simulation script inside the Docker environment. You can specify the number of agents and duration.
    ```bash
    docker-compose build
    docker-compose run --rm agent_runner python scripts/run_experiment.py --agents 5 --duration 60
    ```

3.  **Observe the Outputs:**
    *   **Logs:** `./results/logs/agent_activity.jsonl` (Structured JSON logs)
    *   **Metrics:** `./results/metrics/experiment_results.json` (Precision/Recall Scores)
    *   **Console:** Real-time updates on Training, Detection, Trust Updates, and Topology Changes.

## 📊 Performance (v3.0 - Industrial Grade)

| Metric | Score | Description |
| :--- | :--- | :--- |
| **Recall** | **91.4%** | Highly verified detection of true Global Anomalies. |
| **Precision** | **~62.4%** | Highest precision achieved via Online Learning & Trust Modeling. |
| **Robustness** | **Heartbeats** | Active Failure Detection ensures topology integrity. |

## 📂 Project Structure

```
anomaly_detection_mas/
├── docker/                 # Docker configurations
├── src/
│   ├── agents/            # SPADE Agent implementations (Sensor, Coordinator)
│   ├── behaviors/         # Cyclic/FSM behaviors (Monitoring, Coordination)
│   ├── communication/     # FIPA-ACL message templates
│   ├── data/              # Data generation & Anomaly injection
│   ├── detection/         # ML Logic (Isolation Forest)
│   ├── evaluation/        # Metrics collection & Reporting
│   └── utils/             # Structured Logging
├── scripts/               # Entry points (run_experiment.py)
├── results/               # Experiment artifacts (logs, metrics)
└── docker-compose.yml     # Service Orchestration
```

## 📜 License
This project is for educational purposes as part of the Distributed AI course.
