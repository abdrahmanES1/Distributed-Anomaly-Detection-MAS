import time
import asyncio
from src.agents.sensor_agent import SensorAgent
from src.agents.coordinator_agent import CoordinatorAgent

XMPP_SERVER = "prosody" # Hostname in docker-compose network

async def main():
    print("Starting Multi-Agent Anomaly Detection System...")
    
    # 1. Start Coordinator
    coordinator = CoordinatorAgent(f"coordinator@{XMPP_SERVER}", "password")
    await coordinator.start()
    print("Coordinator started.")
    
    # 2. Start Sensor Agents
    sensors = []
    for i in range(1, 4):
        agent_id = f"sensor{i}@{XMPP_SERVER}"
        agent = SensorAgent(agent_id, "password")
        sensors.append(agent)
    
    # Define Topology (Ring)
    # Sensor 1 <-> Sensor 2
    # Sensor 2 <-> Sensor 3
    # Sensor 3 <-> Sensor 1
    sensor_jids = [s.jid for s in sensors]
    sensors[0].set_neighbors([str(sensor_jids[1]), str(sensor_jids[2])]) # 1 -> 2, 3
    sensors[1].set_neighbors([str(sensor_jids[0]), str(sensor_jids[2])]) # 2 -> 1, 3
    sensors[2].set_neighbors([str(sensor_jids[0]), str(sensor_jids[1])]) # 3 -> 1, 2

    for agent in sensors:
        await agent.start()
        print(f"{agent.agent_id} started.")
        
    print("System running. Press Ctrl+C to stop.")
    
    try:
        while True:
            await asyncio.sleep(1)
            # Here we could systematically inject anomalies if we wanted to automate the test
            
    except KeyboardInterrupt:
        print("Stopping system...")
    finally:
        await coordinator.stop()
        for s in sensors:
            await s.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
