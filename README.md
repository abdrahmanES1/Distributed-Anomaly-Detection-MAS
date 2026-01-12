# Distributed Multi-Agent Anomaly Detection

> **Course:** Distributed Artificial Intelligence (SDA 2024)
> **Status:** Version 1.0 (Functional Prototype)

A robust **Distributed AI (DAI)** system for edge anomaly detection. This project implements a fully decentralized Multi-Agent System (MAS) where autonomous agents monitor local data streams, learn normal behavior using **Unsupervised Machine Learning (Isolation Forests)**, and coordinate via a **Neighborhood Voting Protocol** to reach consensus on global anomalies.

## 🚀 Key Features

*   **Emergent Intelligence:** Global system state is determined solely through local peer-to-peer interactions; no central "brain" exists.
*   **Edge AI:** Each agent runs an independent, lightweight `IsolationForest` model to detect outliers locally.
*   **Robust Coordination:** Implements a FIPA-ACL based voting mechanism (`QUERY`/`INFORM`) to distinguish sensor noise from true system-wide faults.
*   **Fully Containerized:** Built on the **SPADE** framework and **XMPP (Prosody)**, orchestrated via Docker Compose for easy deployment.

## 🛠️ Architecture

The system consists of three main components:
1.  **Sensor Agents:** The intelligent workers. They read data, run ML inference, and vote.
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
    Run the simulation script inside the Docker environment. This handles building images and starting the agent interaction loop.
    ```bash
    docker-compose build
    docker-compose run --rm agent_runner python scripts/run_experiment.py
    ```

3.  **Observe the Logs:**
    You will see the following stages in the terminal:
    *   **Phase 1: Registration** - Agents connect to the XMPP server.
    *   **Phase 2: Training** - Agents gather data to train their local Isolation Forests.
    *   **Phase 3: Monitoring** - Real-time detection runs.
    *   **Phase 4: Anomaly Injection** - A synthetic anomaly is injected, triggering potential alerts.
    *   **Phase 5: Consensus** - Agents verify with neighbors and log `✅ CONFIRMED global anomaly`.

## 📂 Project Structure

```
anomaly_detection_mas/
├── docker/                 # Docker configurations
│   ├── agent/             # Python Agent container
│   └── prosody/           # XMPP Server container
├── src/
│   ├── agents/            # SPADE Agent implementations
│   ├── behaviors/         # Cyclic/FSM behaviors (Monitoring, Coordination)
│   ├── communication/     # FIPA-ACL message templates
│   ├── data/              # Data generation & Anomaly injection
│   └── detection/         # ML Logic (Isolation Forest)
├── scripts/               # Entry points (run_experiment.py)
└── docker-compose.yml     # Service Orchestration
```

## 📜 License
This project is for educational purposes as part of the Distributed AI course.
