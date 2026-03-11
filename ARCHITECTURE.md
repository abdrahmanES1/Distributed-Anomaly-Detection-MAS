# System Architecture: Distributed Multi-Agent Anomaly Detection

This document provides a detailed technical overview of the architecture and internal mechanisms of the Distributed Multi-Agent Anomaly Detection System.

## Architecture Overview

The system is designed as a decentralized network of autonomous agents, each responsible for monitoring a local data source (sensor). Instead of routing all data to a central server for analysis, intelligence is pushed to the edge (the agents), enabling real-time detection and reduced network overhead.

### Core Components

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Agent Logic** | Python / SPADE | Handles agent lifecycle, behaviors, and communication. |
| **Online Learning** | River (ML Library) | Provides real-time, incremental anomaly detection. |
| **Communication** | XMPP (Prosody) | Asynchronous messaging protocol for agent coordination. |
| **Visualization** | Streamlit | Real-time monitoring dashboard and system control. |

---

## 1. Multi-Agent System (MAS)

The system is built on the **SPADE (Smart Python Agent Development Environment)** framework, utilizing the **XMPP** protocol for flexible, asynchronous communication.

### Agent Roles
- **Sensor Agent**: The primary unit of the system. Each agent performs local detection and collaborates with neighbors.
- **Coordinator Agent**: Acts as an observer. It collects alerts from Sensor Agents and exposes system-wide state to the dashboard.

### Topology Management
The system initializes with a structured topology (e.g., ring or mesh). Agents maintain a list of `neighbors` with whom they exchange data and validation requests.

---

## 2. Online Machine Learning (River)

Unlike traditional batch-based ML, this system uses **Online Machine Learning** to adapt to live data streams.

### Half-Space Trees (HST)
The primary algorithm used is River’s **HalfSpaceTrees**, an ensemble method for anomaly detection.
- **Constant Memory**: Complex O(1) memory footprint.
- **No Retraining**: The model updates incrementally with every new data point.
- **Concept Drift**: The sliding window mechanism allows the model to naturally adapt to changing data patterns over time.

---

## 3. Coordination and Consensus

To minimize false positives (common in volatile sensor environments), agents employ a collaborative validation mechanism.

### The Voting Process
1. **Local Detection**: An agent identifies an anomaly in its local stream.
2. **Query Phase**: The agent sends a `QUERY` message to its immediate neighbors.
3. **Neighbor Validation**: Neighbors check their own recent detection history.
4. **Response**: Neighbors reply with `AGREE` if they also observed a surge, otherwise `DISAGREE`.
5. **Consensus**: A high-confidence alert is generated only if a consensus is reached (based on trust and agreement).

### Trust System
Agents maintain a dynamic **Trust Score** for each neighbor:
- **Reward**: Trust increases when a neighbor's vote aligns with the initiator's findings (confirming a grid-wide surge).
- **Grace Period**: Local anomalies (where neighbors disagree) are handled without trust penalties to account for localized sensor faults.
- **Isolation**: If an agent's trust score falls below a critical threshold, it is isolated from the coordination network.

---

## 4. Self-Healing and Resilience

The system is designed to maintain operational integrity in the face of node failures or network partitions.

### Heartbeat Mechanism
Agents periodically exchange `PING/PONG` messages (Heartbeats) with their neighbors.

### Automated Pruning
If a neighbor remains silent beyond a defined timeout period, the agent:
- Identifies the neighbor as "Dead."
- Prunes the neighbor from its active topology.
- Notifies the system to update the global health map.

---

## 5. Deployment and Orchestration

The system is fully containerized using **Docker** and **Docker Compose**, ensuring consistent performance across different environments.

- **Prosody**: Handles the XMPP messaging infrastructure.
- **Agent Runner**: Manages the instantiation and lifecycle of multiple agent instances.
- **Dashboard**: Provides a host-accessible interface for system-wide telemetry and "Mission Control" operations.
