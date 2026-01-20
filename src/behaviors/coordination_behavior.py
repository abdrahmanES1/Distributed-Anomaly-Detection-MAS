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
    Manages agent coordination, including voting sessions, trust scores, and dynamic topology.
    
    Attributes:
        active_sessions (Dict[str, VoteSession]): Currently active voting sessions.
        my_session_id (str): The ID of the session initiated by this agent (if any).
        trust_scores (Dict[str, float]): Trust levels for neighbor agents.
        last_seen (Dict[str, float]): Timestamp of last contact with each neighbor.
        last_heartbeat (float): Timestamp of last heartbeat sent.
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
        Initiates a new voting session for a detected anomaly.
        
        Returns:
            int: Number of neighbors queried.
        """
        # 1. Create Session
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
        
        self.agent.log_info(f"🗳️ Starting voting session {session_id[:8]}...", event_type="voting_start")
        
        # 2. Send Queries
        for neighbor in neighbors:
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
                self.agent.log_info("❌ Failed to decode message body", event_type="error")
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
        """Removes neighbors that haven't responded within timeout."""
        neighbors = getattr(self.agent, 'neighbors', [])
        dead = []
        for n in neighbors:
            last = self.last_seen.get(n, now) 
            if now - last > Settings.COORDINATION.HEARTBEAT_TIMEOUT:
                dead.append(n)
        
        for d in dead:
            self.agent.log_info(f"💀 Neighbor {d} is DEAD (Timeout). Removing.", event_type="prune", target=d)
            self._sever_connection(d) 
            if d in self.last_seen:
                del self.last_seen[d]

    async def handle_query(self, msg: Message, payload: object):
        """
        Respond to a neighbor's query based on local detection state.
        
        Args:
            msg (Message): The received query message.
            payload (CoordinationMessage): The decoded payload.
        """
        is_anomaly = False
        if hasattr(self.agent, 'monitoring'):
             last_time = getattr(self.agent.monitoring, 'last_anomaly_time', 0)
             if (time.time() - last_time) < Settings.COORDINATION.ANOMALY_WINDOW_SECONDS:
                 is_anomaly = True
        
        response_content = "AGREE" if is_anomaly else "DISAGREE"
        
        # Trust Logic (Penalize False Alarms)
        if not is_anomaly:
             sender = str(msg.sender)
             self._update_trust(sender, -Settings.COORDINATION.TRUST_PENALTY)
             
             # Check for severance
             if self.trust_scores.get(sender, 0.5) < Settings.COORDINATION.SEVER_CONNECTION_THRESHOLD:
                 self._sever_connection(sender)
                 # We assume we shouldn't respond if we sever? 
                 # Or respond DISAGREE then cut. Let's send reply for protocol completeness.
        
        reply = create_reply_message(msg, payload.session_id, response_content)
        await self.send(reply)

    async def handle_vote(self, msg: Message, payload: object):
        """
        Process incoming vote for the current active session.
        
        Args:
            msg (Message): The received vote message.
            payload (CoordinationMessage): The decoded payload.
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
            self._update_trust(sender, Settings.COORDINATION.TRUST_REWARD)
            
            if trust > Settings.COORDINATION.CONFIRMATION_THRESHOLD:
                self.agent.log_info(f"✅ CONFIRMED global anomaly via {sender}!", event_type="consensus_reached", peer=sender)
                session.is_active = False 
        else:
            session.disagreements += 1

    def _update_trust(self, peer: str, delta: float):
        """Updates internal trust score for a peer, clamped between min and max."""
        if peer not in self.trust_scores:
            self.trust_scores[peer] = Settings.COORDINATION.INITIAL_TRUST
        
        new_score = self.trust_scores[peer] + delta
        self.trust_scores[peer] = max(
            Settings.COORDINATION.MIN_TRUST_THRESHOLD, 
            min(Settings.COORDINATION.MAX_TRUST_THRESHOLD, new_score)
        )

    def _sever_connection(self, peer: str):
        """Removes a peer from the neighbor list and trust scores."""
        self.agent.log_info(f"✂️ SEVERED CONNECTION to {peer}!", event_type="topology_change", action="sever", target=peer)
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
