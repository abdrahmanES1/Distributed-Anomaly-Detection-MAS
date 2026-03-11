import time
import asyncio
import sys
import argparse
import os
from src.agents.sensor_agent import SensorAgent
from src.agents.coordinator_agent import CoordinatorAgent
from src.evaluation.metrics import MetricCollector

XMPP_SERVER = "prosody" # Hostname in docker-compose network

async def main(num_agents, duration):
    # 0. Clean previous logs for Dashboard
    log_path = "results/logs/agent_activity.jsonl"
    if os.path.exists(log_path):
        print(f"🧹 Clearing previous dashboard logs: {log_path}")
        open(log_path, 'w').close()

    print(f"🚀 Starting Multi-Agent System with {num_agents} agents for {duration} seconds...")
    from src.config.settings import Settings
    Settings.SYSTEM.TOTAL_AGENTS = num_agents
    
    # 1. Start Coordinator
    coordinator = CoordinatorAgent(f"coordinator@{XMPP_SERVER}", "password")
    await coordinator.start()
    print("Coordinator started.")
    
    # 2. Start Sensor Agents
    sensors = []
    for i in range(1, num_agents + 1):
        agent_id = f"sensor{i}@{XMPP_SERVER}"
        agent = SensorAgent(agent_id, "password")
        sensors.append(agent)
    
    # 3. Define Topology (Ring)
    # Each agent connects to next and previous
    sensor_jids = [s.jid for s in sensors]
    for i in range(num_agents):
        prev_agent = sensor_jids[(i - 1) % num_agents]
        next_agent = sensor_jids[(i + 1) % num_agents]
        sensors[i].set_neighbors([str(prev_agent), str(next_agent)])

    # 4. Launch all agents
    for agent in sensors:
        await agent.start()
        
    print(f"System running. Ctrl+C to stop early. Will generate report in {duration}s.")
    
    try:
        # Run simulation for specified duration
        for _ in range(duration):
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("Stopping system via KeyboardInterrupt...")
    finally:
        print("🛑 Stopping agents...")
        await coordinator.stop()
        for s in sensors:
            await s.stop()
            
        print("📊 Generating Metrics Report...")
        collector = MetricCollector()
        collector.generate_report()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Distributed Anomaly Detection Experiment')
    parser.add_argument('--agents', type=int, default=3, help='Number of Sensor Agents')
    parser.add_argument('--duration', type=int, default=100, help='Duration of simulation in seconds')
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args.agents, args.duration))
    except KeyboardInterrupt:
        pass
