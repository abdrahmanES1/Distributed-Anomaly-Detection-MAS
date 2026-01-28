from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
import re

class HealingBehavior(CyclicBehaviour):
    async def run(self):
        # 1. Check health of current neighbors
        # (Ideally we'd ping them, but we rely on correct removal by CoordinationBehavior for now)
        
        # 2. Maintain Minimum Connectivity (Ring Topology = 2 neighbors)
        current_neighbors = getattr(self.agent, 'neighbors', [])
        
        if len(current_neighbors) < 2:
            self.agent.log_info(f"🚑 Topology broken! Neighbors: {len(current_neighbors)}. Initiating active repair...")
            
            # Simple Discovery Strategy: Sequential Scan
            # If I am sensor5, try sensor6, sensor7, etc.
            my_id_match = re.search(r"sensor(\d+)", str(self.agent.jid))
            if my_id_match:
                my_num = int(my_id_match.group(1))
                
                # Scan FULL RING to find a friend (Max robustness)
                # If we limit to 5, a gap of 6 kills the ring.
                # Scanning 1..19 ensures we find anyone alive.
                for offset in range(1, 25): 
                    target_num = my_num + offset
                    # Wrap around 20 (assuming max 20 agents for this demo)
                    # We can use modulo, but specific logic for 1-based indexing:
                    while target_num > 20: 
                        target_num -= 20
                        
                    if target_num == my_num: continue
                    
                    target_jid = f"sensor{target_num}@prosody"
                    
                    # Don't add if already connected
                    if any(target_jid in n for n in current_neighbors):
                        continue
                        
                    # Found a potential candidate.
                    # Since we are desperate (isolated), we add them immediately.
                    # In a real system, we would handshake. Here we assume existence.
                    
                    self.agent.neighbors.append(target_jid)
                    self.agent.log_info(f"🧬 HEALED connection to {target_jid} (Gap Jump: {offset})", event_type="topology_change")
                    
                    # Critical: Log the full set so dashboard updates graph
                    self.agent.log_info(f"Neighbors set: {self.agent.neighbors}")
                    
                    # If we have enough neighbors now, stop scanning
                    if len(self.agent.neighbors) >= 2:
                        break
        
        await asyncio.sleep(5)
