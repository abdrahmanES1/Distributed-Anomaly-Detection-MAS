from spade.behaviour import CyclicBehaviour
from spade.message import Message
import time
import uuid
import json
from dataclasses import dataclass, field
from typing import Set, Dict, Optional
from src.communication.messages import (
    create_query_message, 
    create_reply_message, 
    decode_message,
    PERFORMATIVE_QUERY, 
    PERFORMATIVE_INFORM, 
    ONTOLOGY_COORDINATION
)
from src.config.settings import Settings

@dataclass
class VoteSession:
    session_id: str
    initiator: str
    start_time: float
    agreements: int = 0
    disagreements: int = 0
    pending_voters: Set[str] = field(default_factory=set)
    is_active: bool = True

class CoordinationBehavior(CyclicBehaviour):
    """
    Manages how this agent works with others.
    
    Responsibilities:
    1. Organize voting when an anomaly is found.
    2. Track who we trust (and who we don't).
    3. Maintain network connections (monitor neighbors).
    
    Attributes:
        active_sessions: ongoing votes we know about.
        my_session_id: the vote WE started (if any).
        trust_scores: how much we trust each neighbor (0.0 to 1.0).
        last_seen: when we last heard from a neighbor.
    """
    
    async def on_start(self):
        """Initializes state variables on behavior start."""
        self.active_sessions: Dict[str, VoteSession] = {} 
        self.my_session_id: Optional[str] = None 
        
        # Trust & Topology
        self.trust_scores: Dict[str, float] = {}
        self.last_seen: Dict[str, float] = {}
        self.last_heartbeat: float = 0.0
        
        for neighbor in getattr(self.agent, 'neighbors', []):
            self.trust_scores[neighbor] = Settings.COORDINATION.INITIAL_TRUST
            self.last_seen[neighbor] = time.time()

    async def start_voting(self) -> int:
        """
        Calculates how many neighbors to ask for a vote.
        Triggered when we detect an anomaly locally.
        """
        # 1. Start a new voting session
        session_id = str(uuid.uuid4())
        self.my_session_id = session_id
        
        neighbors = getattr(self.agent, 'neighbors', [])
        session = VoteSession(
            session_id=session_id,
            initiator=str(self.agent.jid),
            start_time=time.time(),
            pending_voters=set(neighbors)
        )
        self.active_sessions[session_id] = session
        
        self.agent.log_info(f"Starting voting session {session_id[:8]}...", event_type="voting_start")
        
        # 2. Ask all neighbors: "Do you see this too?"
        for neighbor in neighbors:
            # Initialize trust if new neighbor
            if neighbor not in self.trust_scores:
                self.trust_scores[neighbor] = Settings.COORDINATION.INITIAL_TRUST
                
            msg = create_query_message(neighbor, session_id)
            await self.send(msg)
            
        return len(neighbors)

    async def run(self):
        """Main behavior loop: handles messages, heartbeats, and cleanup."""
        # 1. Self-Healing & Maintenance
        now = time.time()
        await self._send_heartbeats(now)
        self._prune_dead_neighbors(now)
        self._cleanup_sessions(now)
        
        # 2. Process Messages
        msg = await self.receive(timeout=1.0)
        
        if not msg:
            return

        sender = str(msg.sender)
        self.last_seen[sender] = now # Update liveness
        
        # 3. Handle System Messages (Heartbeats)
        if msg.get_metadata("ontology") == "heartbeat":
            if msg.body == "PING":
                # Respond with PONG
                reply = Message(to=sender)
                reply.body = "PONG"
                reply.set_metadata("ontology", "heartbeat")
                await self.send(reply)
            return

        # 4. Handle Coordination Messages
        if msg.get_metadata("ontology") == ONTOLOGY_COORDINATION:
            payload = decode_message(msg.body)
            if not payload:
                self.agent.log_info("Failed to decode message body", event_type="error")
                return

            if payload.type == "QUERY":
                await self.handle_query(msg, payload)
            elif payload.type == "VOTE":
                await self.handle_vote(msg, payload)

    async def _send_heartbeats(self, now: float):
        """Sends PING messages to neighbors if interval has passed."""
        if now - self.last_heartbeat > Settings.COORDINATION.HEARTBEAT_INTERVAL:
            self.last_heartbeat = now
            for neighbor in getattr(self.agent, 'neighbors', []):
                msg = Message(to=str(neighbor))
                msg.body = "PING"
                msg.set_metadata("ontology", "heartbeat")
                await self.send(msg)

    def _prune_dead_neighbors(self, now: float):
        """Removes neighbors who stopped responding (Timeouts)."""
        neighbors = getattr(self.agent, 'neighbors', [])
        dead = []
        for n in neighbors:
            last = self.last_seen.get(n, now) 
            # If silence > timeout, mark as dead
            if now - last > Settings.COORDINATION.HEARTBEAT_TIMEOUT:
                dead.append(n)
        
        for d in dead:
            self.agent.log_info(f"Neighbor {d} died (Timeout). Removing.", event_type="prune", target=d)
            self._sever_connection(d) 
            if d in self.last_seen:
                del self.last_seen[d]

    async def handle_query(self, msg: Message, payload: object):
        """
        Another agent asked: "I have a voltage surge! Do you see it too?"
        We check our own recent history to answer.
        """
        is_anomaly = False
        if hasattr(self.agent, 'monitoring'):
             # Did we see a voltage surge recently? (e.g., last 3 seconds)
             last_time = getattr(self.agent.monitoring, 'last_anomaly_time', 0)
             if (time.time() - last_time) < Settings.COORDINATION.ANOMALY_WINDOW_SECONDS:
                 is_anomaly = True
        
        # Determine our vote: "AGREE" means we see it too (Grid-Wide). "DISAGREE" means we don't (Local).
        response_content = "AGREE" if is_anomaly else "DISAGREE"
        
        # IMPORTANT: We no longer penalize them for a "DISAGREE" vote!
        # A localized anomaly (e.g. tree on a line) is valid even if neighbors don't see it.
        # We ONLY penalize if they are actively trying to deceive the network (e.g. claiming to be dead but sending msgs)
        
        reply = create_reply_message(msg, payload.session_id, response_content)
        await self.send(reply)

    async def handle_vote(self, msg: Message, payload: object):
        """
        Received a vote ("AGREE" or "DISAGREE") from a neighbor regarding our voltage surge.
        """
        session_id = payload.session_id
        
        if session_id != self.my_session_id:
            return 
            
        session = self.active_sessions.get(session_id)
        if not session or not session.is_active:
            return

        sender = str(msg.sender)
        vote = payload.content
        trust = self.trust_scores.get(sender, Settings.COORDINATION.INITIAL_TRUST)
        
        self.agent.log_info(f"Received VOTE from {sender}: {vote}", event_type="voting_response", vote=vote)
        
        if sender in session.pending_voters:
            session.pending_voters.remove(sender)
            
        if vote == "AGREE":
            session.agreements += 1
            # They agreed with us -> This is a Grid-Wide Surge! Trust increases
            self._update_trust(sender, Settings.COORDINATION.TRUST_REWARD)
            
            # If trusted neighbor agrees, we escalate to a Grid-Wide Alert!
            if trust > Settings.COORDINATION.CONFIRMATION_THRESHOLD:
                self.agent.log_info(f"ESCALATION: {sender} agrees! GRID-WIDE SURGE DETECTED!", event_type="consensus_reached", peer=sender)
                session.is_active = False 
        else:
            session.disagreements += 1
            # They disagreed -> It's a localized event. No trust penalty applied.
            self.agent.log_info(f"LOCAL: Neighbors disagree. Surge is isolated to local sector.", event_type="local_anomaly_confirmed")
            
            # Note: We do NOT penalize trust here. Local anomalies are normal in a Smart Grid (e.g. local faults).
            # The session remains active until timeout or consensus is reached.

    def _update_trust(self, peer: str, delta: float):
        """Adjusts trust score securely (clamps between 0.0 and 1.0)."""
        if peer not in self.trust_scores:
            self.trust_scores[peer] = Settings.COORDINATION.INITIAL_TRUST
        
        new_score = self.trust_scores[peer] + delta
        # Ensure score stays within bounds [Min, Max]
        self.trust_scores[peer] = max(
            Settings.COORDINATION.MIN_TRUST_THRESHOLD, 
            min(Settings.COORDINATION.MAX_TRUST_THRESHOLD, new_score)
        )

    def _sever_connection(self, peer: str):
        """Cuts off a neighbor (removes from list and deletes trust data)."""
        self.agent.log_info(f"SEVERING connection to {peer}!", event_type="topology_change", action="sever", target=peer)
        if peer in self.agent.neighbors:
            self.agent.neighbors.remove(peer)
        if peer in self.trust_scores:
            self.trust_scores.pop(peer)

    def _cleanup_sessions(self, now: float):
        """Removes timed-out voting sessions."""
        to_remove = []
        for sid, session in self.active_sessions.items():
            if now - session.start_time > Settings.COORDINATION.VOTE_TIMEOUT:
                to_remove.append(sid)
        
        for sid in to_remove:
            del self.active_sessions[sid]
            if sid == self.my_session_id:
                self.my_session_id = None
