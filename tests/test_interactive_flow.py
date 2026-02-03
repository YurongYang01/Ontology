import unittest
import asyncio
from unittest.mock import MagicMock, patch
from agent_system.integration_module import AgentIntegrationModule
from agent_system.generation_module import AnswerGenerationModule
from agent_system.query_module import OntologyQueryModule
from agent_system.tool_manager import ToolManager

class TestInteractiveFlow(unittest.TestCase):
    def setUp(self):
        self.mock_query = MagicMock(spec=OntologyQueryModule)
        self.mock_query.query_by_type.return_value = []
        
        self.mock_gen = MagicMock(spec=AnswerGenerationModule)
        self.mock_tool = MagicMock(spec=ToolManager)
        self.mock_tool.get_tool_descriptions.return_value = "No tools"
        
        self.agent = AgentIntegrationModule(self.mock_query, self.mock_gen, self.mock_tool)

    def test_multi_turn_history(self):
        async def run_test():
            # Setup mocks
            async def mock_decide(*args, **kwargs):
                return None
            
            async def mock_generate(question, parsed_results, context, chat_history=None):
                return f"Answer to {question}"
            
            self.mock_gen.decide_tool_call.side_effect = mock_decide
            self.mock_gen.generate_answer.side_effect = mock_generate
            
            # Turn 1
            q1 = "Hi"
            a1 = await self.agent.process_query(q1)
            self.assertEqual(a1, "Answer to Hi")
            self.assertEqual(len(self.agent.chat_history), 1)
            self.assertEqual(self.agent.chat_history[0], (q1, a1))
            
            # Turn 2
            q2 = "Who are you?"
            a2 = await self.agent.process_query(q2)
            self.assertEqual(a2, "Answer to Who are you?")
            self.assertEqual(len(self.agent.chat_history), 2)
            self.assertEqual(self.agent.chat_history[1], (q2, a2))
            
            # Verify generate_answer was called with correct history
            # The last call should have the history including the first turn
            call_args = self.mock_gen.generate_answer.call_args_list
            self.assertEqual(len(call_args), 2)
            
            # Check 2nd call arguments
            _, kwargs2 = call_args[1]
            history_arg = kwargs2.get('chat_history')
            self.assertEqual(len(history_arg), 1)
            self.assertEqual(history_arg[0], (q1, a1))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_test())
        loop.close()

    def test_reset_history(self):
        self.agent.chat_history = [("Q", "A")]
        self.agent.reset_history()
        self.assertEqual(len(self.agent.chat_history), 0)

if __name__ == "__main__":
    unittest.main()
