from spade.behaviour import CyclicBehaviour
from spade.message import Message
import time
from src.communication.messages import (
    create_query_message, 
    create_reply_message, 
    create_alert_message,
    PERFORMATIVE_QUERY, 
    PERFORMATIVE_INFORM, 
    ONTOLOGY_COORDINATION
)

class CoordinationBehavior(CyclicBehaviour):
    async def on_start(self):
        self.votes = {} # msg_id -> count
        self.pending_requests = set()

    async def start_voting(self):
        """Initiates the voting process with neighbors."""
        print(f"[{self.agent.agent_id}] 🗳️ Starting neighborhood voting...")
        neighbors = getattr(self.agent, 'neighbors', [])
        
        for neighbor in neighbors:
            msg = create_query_message(neighbor)
            await self.send(msg)
            
        return len(neighbors)

    async def run(self):
        msg = await self.receive(timeout=10)
        
        if not msg:
            return

        if msg.get_metadata("ontology") == ONTOLOGY_COORDINATION:
            performative = msg.get_metadata("performative")
            
            if performative == PERFORMATIVE_QUERY:
                await self.handle_query(msg)
            elif performative == PERFORMATIVE_INFORM:
                await self.handle_response(msg)

    async def handle_query(self, msg):
        """Respond to a neighbor's query based on local status."""
        # Check local detection state
        is_anomaly = False
        if hasattr(self.agent, 'monitoring'):
             last_time = getattr(self.agent.monitoring, 'last_anomaly_time', 0)
             if (time.time() - last_time) < 2.0: # 2 seconds window
                 is_anomaly = True
        
        response_content = "AGREE" if is_anomaly else "DISAGREE"
        print(f"[{self.agent.agent_id}] Received QUERY from {msg.sender}. Replying: {response_content}")
        
        reply = create_reply_message(msg, response_content)
        await self.send(reply)

    async def handle_response(self, msg):
        """Collect votes and determine consensus."""
        print(f"[{self.agent.agent_id}] Received VOTE from {msg.sender}: {msg.body}")
        
        # Simple Logic: If we receive an AGREE, we increment confirmation
        # In a real system, we would track specific voting sessions IDs
        
        if msg.body == "AGREE":
            print(f"[{self.agent.agent_id}] ✅ CONFIRMED global anomaly with peer {msg.sender}!")
            # Here we could send a final alert to coordinator
            # alert = create_alert_message("coordinator@prosody", f"Confirmed Anomaly by {self.agent.agent_id}")
            # await self.send(alert)
