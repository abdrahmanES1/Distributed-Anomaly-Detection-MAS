
import unittest
import json
import asyncio
from unittest.mock import MagicMock, AsyncMock
from src.behaviors.coordination_behavior import CoordinationBehavior, VoteSession
from src.communication.messages import CoordinationMessage, decode_message

class MockAgent:
    def __init__(self):
        self.jid = "me@server"
        self.neighbors = ["neighbor@server"]
        self.monitoring = MagicMock()
        self.log_info = MagicMock()

class TestRobustCoordination(unittest.IsolatedAsyncioTestCase):
    async def test_start_voting_creates_session(self):
        agent = MockAgent()
        behavior = CoordinationBehavior()
        behavior.agent = agent
        behavior.send = AsyncMock()
        
        await behavior.on_start()
        await behavior.start_voting()
        
        # Check Session Logic
        self.assertIsNotNone(behavior.my_session_id)
        self.assertIn(behavior.my_session_id, behavior.active_sessions)
        session = behavior.active_sessions[behavior.my_session_id]
        self.assertIsInstance(session, VoteSession)
        self.assertTrue(session.is_active)
        
        # Check Message Content
        behavior.send.assert_called()
        call_args = behavior.send.call_args[0]
        msg = call_args[0]
        
        print(f"Sent Message Body: {msg.body}")
        
        # Verify JSON Structure
        payload = decode_message(msg.body)
        self.assertIsNotNone(payload)
        self.assertEqual(payload.type, "QUERY")
        self.assertEqual(payload.session_id, behavior.my_session_id)
        print("✅ Voting Session started and Query is valid JSON.")

    async def test_vote_processing(self):
        agent = MockAgent()
        behavior = CoordinationBehavior()
        behavior.agent = agent
        behavior.send = AsyncMock() # Fix: Mock send to avoid agent.container error
        
        await behavior.on_start()
        await behavior.start_voting()
        
        session_id = behavior.my_session_id
        
        # Create a Mock Incoming Vote
        vote_payload = CoordinationMessage(
            type="VOTE",
            session_id=session_id,
            content="AGREE"
        )
        
        mock_msg = MagicMock()
        mock_msg.sender = "neighbor@server"
        mock_msg.body = json.dumps(vote_payload.__dict__)
        
        # Process Vote
        await behavior.handle_vote(mock_msg, vote_payload)
        
        session = behavior.active_sessions[session_id]
        self.assertEqual(session.agreements, 1)
        print("✅ Vote processed and Agreement counted.")

if __name__ == '__main__':
    unittest.main()
