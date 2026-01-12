from spade.template import Template
from spade.message import Message

# Ontologies
ONTOLOGY_MONITOR = "monitoring"
ONTOLOGY_COORDINATION = "coordination"

# Performatives
PERFORMATIVE_INFORM = "inform" # Used for alerts and replies
PERFORMATIVE_QUERY = "query_ref" # Used for checking neighbors

def create_alert_message(to_jid, content):
    msg = Message(to=str(to_jid))
    msg.set_metadata("performative", PERFORMATIVE_INFORM)
    msg.set_metadata("ontology", ONTOLOGY_MONITOR)
    msg.body = content
    return msg

def create_query_message(to_jid):
    msg = Message(to=str(to_jid))
    msg.set_metadata("performative", PERFORMATIVE_QUERY)
    msg.set_metadata("ontology", ONTOLOGY_COORDINATION)
    msg.body = "check_anomaly"
    return msg

def create_reply_message(original_msg, content):
    msg = original_msg.make_reply()
    msg.set_metadata("performative", PERFORMATIVE_INFORM)
    msg.set_metadata("ontology", ONTOLOGY_COORDINATION)
    msg.body = content
    return msg
