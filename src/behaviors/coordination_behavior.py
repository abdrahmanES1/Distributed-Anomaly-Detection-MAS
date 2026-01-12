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
        # Trust Scores: JID -> Score (0.0 to 1.0, default 0.5)
        self.trust_scores = {}
        for neighbor in getattr(self.agent, 'neighbors', []):
            self.trust_scores[neighbor] = 0.5

    async def start_voting(self):
        """Initiates the voting process with neighbors."""
        # Reset current vote session
        self.current_vote_session = {"agreements": 0, "disagreements": 0, "voters": []}
        
        self.agent.log_info("🗳️ Starting neighborhood voting...", event_type="voting_start")
        neighbors = getattr(self.agent, 'neighbors', [])
        
        for neighbor in neighbors:
            # Ensure trust score initialized
            if neighbor not in self.trust_scores:
                self.trust_scores[neighbor] = 0.5
                
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

        else:
            # DISAGREE
            # PUNISHMENT LOGIC:
            # If I detected an anomaly (and asked for votes), but they DISAGREE...
            # This logic is tricky. If I am right, they are "blind". If I am wrong, they are "correct".
            # For this prototype, we punish "Spamming".
            # Better logic: If I receive an AGREE vote when I did NOT detect anything.
            pass
            
            
    async def handle_query(self, msg):
        """Respond to a neighbor's query based on local status."""
        # Check local detection state
        is_anomaly = False
        if hasattr(self.agent, 'monitoring'):
             last_time = getattr(self.agent.monitoring, 'last_anomaly_time', 0)
             if (time.time() - last_time) < 3.0: # 3.0 second window (Robust to 2s drift)
                 is_anomaly = True
        
        response_content = "AGREE" if is_anomaly else "DISAGREE"
        
        # PUNISHMENT FOR FALSE POSITIVES (Dynamic Topology):
        # If I see nothing (DISAGREE), but they are querying me because they think there's a fire...
        # They might be noisy. We decrease trust slightly.
        # Note: This is harsh. Ideally, we wait to see if *others* agree with them.
        # But for 'Self-Healing' demo, this works: "Don't bother me with false alarms".
        
        if not is_anomaly:
             sender = str(msg.sender)
             if sender not in self.trust_scores:
                 self.trust_scores[sender] = 0.5
             
             self.trust_scores[sender] -= 0.05 # Production Punishment
             self.agent.log_info(f"Trust DECREASED for {sender} (False Alarm Query): {self.trust_scores[sender]:.2f}")
             
             # SEVERANCE LOGIC
             if self.trust_scores[sender] < 0.2:
                 self.agent.log_info(f"✂️ SEVERED CONNECTION to {sender} due to Low Trust!", event_type="topology_change", action="sever", peer=sender)
                 if sender in self.agent.neighbors:
                     self.agent.neighbors.remove(sender)
                     self.trust_scores.pop(sender) # Forget them
        
        self.agent.log_info(f"Received QUERY from {msg.sender}. Replying: {response_content}", 
                           event_type="voting_query", sender=str(msg.sender), reply=response_content)
        
        reply = create_reply_message(msg, response_content)
        await self.send(reply)

    async def handle_response(self, msg):
        """Collect votes and determine consensus using TRUST SCORES."""
        sender = str(msg.sender)
        vote = msg.body
        
        # Ensure sender has trust score
        if sender not in self.trust_scores:
            self.trust_scores[sender] = 0.5
            
        trust = self.trust_scores[sender]
        
        self.agent.log_info(f"Received VOTE from {sender} (Trust: {trust:.2f}): {vote}", 
                           event_type="voting_response", sender=sender, vote=vote, trust_score=trust)
        
        # We need to track the session to make a decision
        # Ideally, we wait for all votes, but for prototype we process continuously
        
        if vote == "AGREE":
            # REWARD: If we also think it's an anomaly, trust them more
            # Only if we initiated the vote (meaning we also detected it)
            if hasattr(self, 'current_vote_session'):
                 self.trust_scores[sender] = min(1.0, trust + 0.05)
                 self.agent.log_info(f"Trust INCREASED for {sender}: {self.trust_scores[sender]:.2f}")
            
            # Weighted Voting Decision
            # If (High Trust Neighbor) Agrees -> Confirm
            if trust > 0.4: # Only listen to reasonably trusted agents
                self.agent.log_info(f"✅ CONFIRMED global anomaly with peer {sender}!", 
                                   event_type="consensus_reached", peer=sender)
        else:
            # DISAGREE
            # PUNISH: They disagreed with us (assuming we are right)
            # This is a simplification; ideally we punish only if MAJORITY agrees and they don't.
            pass
