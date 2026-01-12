# Distributed Multi-Agent Anomaly Detection

> **Course:** Distributed Artificial Intelligence (SDA 2024)
> **Status:** Version 2.0 (Professional Grade)

A robust **Distributed AI (DAI)** system for edge anomaly detection. This project implements a fully decentralized Multi-Agent System (MAS) where autonomous agents monitor local data streams, learn normal behavior using **Unsupervised Machine Learning (Isolation Forests)**, and coordinate via a **Meritocratic Consensus Protocol** to reach consensus on global anomalies.

## 🚀 Key Features

*   **Emergent Intelligence:** Global system state is determined solely through local peer-to-peer interactions; no central "brain" exists.
*   **Edge AI:** Each agent runs an independent, lightweight `IsolationForest` model to detect outliers locally.
*   **Decorrelation:** Implementation of **Phase Shift Diversity** to prevent "Echo Chamber" correlated errors among agents.
*   **Trust Modeling:** A dynamic **Meritocratic Reputation System** where agents weigh votes based on the reliability of their neighbors.
*   **Self-Healing Network:** Agents automatically **sever connections** with neighbors who consistently report false positives (Dynamic Topology).
*   **Fully Containerized:** Built on the **SPADE** framework and **XMPP (Prosody)**, orchestrated via Docker Compose for easy deployment.

## 🛠️ Architecture

The system consists of three main components:
1.  **Sensor Agents:** The intelligent workers. They read data, run ML inference, track neighbor trust, and vote.
2.  **Coordinator Agent:** An optional observer that logs finalized global alerts.
3.  **XMPP Server:** The communication backbone (Prosody) facilitating secure message passing.

### Technologies
*   **Language:** Python 3.9
*   **Framework:** SPADE (Smart Python Agent Development Environment)
*   **ML Library:** Scikit-Learn
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

## 📊 Performance (v2.0)

| Metric | Score | Description |
| :--- | :--- | :--- |
| **Recall** | **100%** | The system detected all injected global anomalies. |
| **Precision** | **~69%** | High robustness against local noise due to Trust Modeling. |
| **Robustness** | **Self-Healing** | Network automatically isolates noisy agents. |

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
