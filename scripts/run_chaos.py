import time
import asyncio
import sys
import argparse
import random
import os
from src.agents.sensor_agent import SensorAgent
from src.agents.coordinator_agent import CoordinatorAgent
from src.evaluation.metrics import MetricCollector

XMPP_SERVER = "prosody" 

async def main(num_agents, duration):
    # 0. Clean previous logs for Dashboard
    log_path = "results/logs/agent_activity.jsonl"
    if os.path.exists(log_path):
        print(f"🧹 Clearing previous dashboard logs: {log_path}")
        open(log_path, 'w').close()

    print(f"🚀 Starting CHAOS Mode with {num_agents} agents for {duration} seconds...")
    print("🔥 Agents will be terminated randomly during execution!")
    
    from src.config.settings import Settings
    Settings.SYSTEM.TOTAL_AGENTS = num_agents
    
    # 1. Start Coordinator
    coordinator = CoordinatorAgent(f"coordinator@{XMPP_SERVER}", "password")
    await coordinator.start()
    
    # 2. Start Sensor Agents
    sensors = []
    for i in range(1, num_agents + 1):
        agent_id = f"sensor{i}@{XMPP_SERVER}"
        agent = SensorAgent(agent_id, "password")
        sensors.append(agent)
    
    # 3. Define Topology (Ring)
    sensor_jids = [s.jid for s in sensors]
    for i in range(num_agents):
        prev_agent = sensor_jids[(i - 1) % num_agents]
        next_agent = sensor_jids[(i + 1) % num_agents]
        sensors[i].set_neighbors([str(prev_agent), str(next_agent)])

    # 4. Launch all agents
    for agent in sensors:
        await agent.start()
        
    print(f"✅ System stable. Chaos Monkey sleeping for 45s...")
    
    start_time = time.time()
    chaos_triggered = False
    
    try:
        while time.time() - start_time < duration:
            # CHAOS TRIGGER at T+45s
            if not chaos_triggered and (time.time() - start_time > 45):
                chaos_triggered = True
                print("\n\n🔥🔥🔥 CHAOS MONKEY ATTACK! 🔥🔥🔥")
                
                # Kill 25% of agents
                num_to_kill = max(1, int(num_agents * 0.25))
                victims = random.sample(sensors, num_to_kill)
                
                for victim in victims:
                    print(f"☠️ TERMINATING AGENT: {victim.jid}")
                    # Log the death so dashboard sees it
                    victim.log_info(f"💀 AGENT KILLED BY CHAOS MONKEY", event_type="chaos_death")
                    await victim.stop()
                    sensors.remove(victim) # Remove from active list
                    
                print(f"📉 Killed {num_to_kill} agents. Surviving count: {len(sensors)}")
                print("Observe the Dashboard for topology updates...\n")

            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("Stopping system via KeyboardInterrupt...")
    finally:
        print("🛑 Stopping remaining agents...")
        await coordinator.stop()
        for s in sensors:
            if s.is_alive():
                await s.stop()
            
        print("📊 Generating Metrics Report...")
        collector = MetricCollector()
        collector.generate_report()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Distributed Anomaly Detection CHAOS Experiment')
    parser.add_argument('--agents', type=int, default=20, help='Number of Sensor Agents')
    parser.add_argument('--duration', type=int, default=90, help='Duration of simulation in seconds')
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args.agents, args.duration))
    except KeyboardInterrupt:
        pass
