import json
from dataclasses import dataclass, asdict
from typing import Optional
from spade.message import Message

# Ontologies
ONTOLOGY_MONITOR = "monitoring"
ONTOLOGY_COORDINATION = "coordination"

# Performatives
PERFORMATIVE_INFORM = "inform" 
PERFORMATIVE_QUERY = "query_ref" 

@dataclass
class CoordinationMessage:
    type: str # "QUERY" or "VOTE"
    session_id: str
    content: str # "check_anomaly", "AGREE", "DISAGREE"
    confidence: float = 1.0
    timestamp: float = 0.0

def create_query_message(to_jid, session_id):
    msg = Message(to=str(to_jid))
    msg.set_metadata("performative", PERFORMATIVE_QUERY)
    msg.set_metadata("ontology", ONTOLOGY_COORDINATION)
    
    payload = CoordinationMessage(
        type="QUERY",
        session_id=session_id,
        content="check_anomaly"
    )
    msg.body = json.dumps(asdict(payload))
    return msg

def create_reply_message(original_msg, session_id, vote_content):
    msg = original_msg.make_reply()
    msg.set_metadata("performative", PERFORMATIVE_INFORM)
    msg.set_metadata("ontology", ONTOLOGY_COORDINATION)
    
    payload = CoordinationMessage(
        type="VOTE",
        session_id=session_id,
        content=vote_content
    )
    msg.body = json.dumps(asdict(payload))
    return msg

def decode_message(msg_body: str) -> Optional[CoordinationMessage]:
    try:
        data = json.loads(msg_body)
        return CoordinationMessage(**data)
    except json.JSONDecodeError:
        return None
