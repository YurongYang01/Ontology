import unittest
import asyncio
import os
import json
from unittest.mock import MagicMock, patch
from agent_system.query_module import OntologyQueryModule
from agent_system.parsing_module import ResultParsingModule
from agent_system.tool_manager import ToolManager
from ontology_tool.core.manager import OntologyManager

class TestAgentSystem(unittest.TestCase):
    def setUp(self):
        # Setup a temporary graph for testing
        self.test_graph = "tests/test_graph.jsonl"
        self.manager = OntologyManager(graph_path=self.test_graph)
        self.manager.clear_graph()
        
        # Add some test data
        self.manager.create_entity("Person", {"name": "Alice", "email": "alice@test.com"}, "p_alice")
        self.manager.create_entity("Task", {"title": "Test Task", "status": "open"}, "t_test")
        self.manager.create_relation("p_alice", "has_task", "t_test")

        self.query_module = OntologyQueryModule(self.manager)
        self.tool_manager = ToolManager()

    def tearDown(self):
        if os.path.exists(self.test_graph):
            os.remove(self.test_graph)

    def test_query_by_type(self):
        results = self.query_module.query_by_type("Person")
        self.assertTrue(len(results) > 0)
        # Check if Alice is in results
        names = [r.get("value") for r in results if r.get("prop") == "name"]
        self.assertIn("Alice", names)

    def test_parsing_results(self):
        results = [{"id": "p_alice", "name": "Alice"}]
        parsed = ResultParsingModule.parse_query_results(results)
        self.assertIn("Alice", parsed)
        self.assertIn("p_alice", parsed)

    def test_tool_calculator(self):
        result = self.tool_manager.call_tool("calculator", expression="10 + 20")
        self.assertEqual(result, "30")

    def test_tool_calculator_invalid(self):
        result = self.tool_manager.call_tool("calculator", expression="10 + abc")
        self.assertIn("错误", result)

    @patch('agent_system.generation_module.AnswerGenerationModule.generate_answer', new_callable=MagicMock)
    @patch('agent_system.generation_module.AnswerGenerationModule.decide_tool_call', new_callable=MagicMock)
    def test_integration_flow(self, mock_decide, mock_generate):
        from agent_system.integration_module import AgentIntegrationModule
        from agent_system.generation_module import AnswerGenerationModule
        
        # Setup async mocks
        async def mock_gen_func(*args, **kwargs):
            return "This is a mock answer."
        
        async def mock_decide_func(*args, **kwargs):
            return None
            
        mock_generate.side_effect = mock_gen_func
        mock_decide.side_effect = mock_decide_func
        
        gen_module = AnswerGenerationModule()
        agent = AgentIntegrationModule(self.query_module, gen_module, self.tool_manager)
        
        # We need to run the async method
        loop = asyncio.get_event_loop()
        answer = loop.run_until_complete(agent.process_query("Who is Alice?"))
        
        self.assertEqual(answer, "This is a mock answer.")

if __name__ == "__main__":
    unittest.main()
