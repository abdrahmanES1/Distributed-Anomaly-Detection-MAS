import time
import json
import os
import subprocess
import sys

JOB_FILE = "jobs/request.json"
LAST_PROCESSED = 0

def run_command(cmd):
    """Executes a shell command."""
    print(f"⚙️ EXECUTING: {cmd}")
    subprocess.Popen(cmd, shell=True)

def stop_simulation():
    print("🛑 STOPPING SIMULATION...")
    # This might need to be more robust to find the correct container/process
    # But usually docker-compose run --rm cleans itself up, or we can kill the container
    subprocess.run("docker stop $(docker ps -q --filter ancestor=anomaly_detection_mas-agent_runner)", shell=True)

def process_job(job):
    cmd_type = job.get("command")
    agents = job.get("agents", 20)
    
    if cmd_type == "start":
        print(f"🚀 STARTING SIMULATION ({agents} agents)...")
        run_command(f"docker-compose run --rm agent_runner python scripts/run_experiment.py --agents {agents} --duration 300")
        
    elif cmd_type == "chaos":
        print(f"🔥 STARTING CHAOS MODE ({agents} agents)...")
        run_command(f"docker-compose run --rm agent_runner python scripts/run_chaos.py --agents {agents} --duration 300")
        
    elif cmd_type == "stop":
        stop_simulation()

def main():
    global LAST_PROCESSED
    print("👀 JOB RUNNER STARTED. Monitoring 'jobs/request.json'...")
    print("👉 Use the Dashboard 'Mission Control' to trigger actions.")
    
    # Ensure job file exists
    if not os.path.exists(JOB_FILE):
        with open(JOB_FILE, 'w') as f:
            json.dump({}, f)

    while True:
        try:
            if os.path.exists(JOB_FILE):
                with open(JOB_FILE, 'r') as f:
                    try:
                        job = json.load(f)
                    except json.JSONDecodeError:
                        continue
                
                timestamp = job.get("timestamp", 0)
                
                if timestamp > LAST_PROCESSED:
                    process_job(job)
                    LAST_PROCESSED = timestamp
                    
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting Job Runner...")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
