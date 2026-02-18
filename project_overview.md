# Project Overview: Distributed Anomaly Detection MAS

## 🎯 **Project Goal**
A production-ready **Distributed Multi-Agent System (MAS)** designed to detect anomalies in sensor networks. The system moves beyond traditional centralized batch processing by deploying independent, intelligent agents that learn and coordinate in real-time.

---

## 🏗️ **Core Architecture**

### **1. Agent Framework (SPADE)**
- **Decentralized Agents**: Built using **SPADE (Smart Python Agent Development Environment)**.
- **Communication**: Agents communicate via **XMPP** (Extensible Messaging and Presence Protocol) using a **Prosody** server.
- **Roles**:
    - **Sensor Agents**: Monitor data streams, detect anomalies locally, and collaborate with neighbors.
    - **Coordinator Agent**: Oversees global system state (optional/informational role).

### **2. Online Machine Learning (River)**
- **Algorithm**: **Half-Space Trees (HST)** implementation from the **River** library.
- **Why River?**:
    - **True Online Learning**: The model updates incrementally with each data point ($O(1)$ complexity).
    - **No Batch Training**: Eliminates the need for collecting large historical datasets before deployment.
    - **Concept Drift**: Naturally adapts to changing data distributions over time.

### **3. Coordination & Trust System**
- **Voting Protocol**: When an agent detects an anomaly, it initiates a peer-to-peer voting session with neighbors to confirm the finding, reducing false positives.
- **Dynamic Trust Scores**:
    - Agents track the reliability of their neighbors.
    - **Agreement** increases trust; **Disagreement** decreases trust.
    - **Isolation**: Agents with low trust scores (below 0.2) or unresponsive agents are automatically severed from the network to maintain system integrity.
    - *Configurable*: `TRUST_PENALTY` set to `0.03` for fault tolerance.

### **4. System Resilience**
- **Self-Healing Topology**: The network (Ring/Mesh) automatically repairs itself when agents die or get disconnected.
- **Chaos Engineering**: Built-in "Chaos Mode" capabilities to test resilience by randomly terminating agents during execution.
- **Heartbeat Mechanism**: Continuous ping/pong checks with latency tracking to monitor neighbor health and network performance.

---

## 🖥️ **"War Room" Dashboard**
A real-time monitoring interface built with **Streamlit**:
- **Fleet Status**: Live health and status table for all 20+ active agents.
- **Metrics**: Real-time visualization of trust scores, anomaly signals, and voting measurements.
- **Mission Control**: Interface to initialize simulations, trigger chaos events, or emergency stop the system.

---

## 🛠️ **Tech Stack**
| Component | Technology | Use Case |
| :--- | :--- | :--- |
| **Language** | Python 3.9+ | Core logic |
| **Agents** | SPADE | Agent communication & lifecycle |
| **ML** | River | Online Anomaly Detection |
| **Server** | Prosody (XMPP) | Messaging backbone |
| **UI** | Streamlit + Altair | Real-time Dashboard |
| **Infra** | Docker & Compose | Orchestration & Deployment |

---

## 📊 **Key Metrics**
- **Latency**: Mean consensus time < 200ms.
- **Scalability**: Tested with 20 concurrent agents.
- **Resilience**: Operational up to 30% node loss.
