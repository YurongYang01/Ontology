import logging
from .query_module import OntologyQueryModule
from .parsing_module import ResultParsingModule
from .generation_module import AnswerGenerationModule
from .tool_manager import ToolManager

logger = logging.getLogger(__name__)

class AgentIntegrationModule:
    """
    Orchestrates the query, parsing, tool calling, and answer generation.
    Maintains conversation history for multi-turn dialogue.
    """
    def __init__(self, query_module: OntologyQueryModule, generation_module: AnswerGenerationModule, tool_manager: ToolManager):
        self.query_module = query_module
        self.generation_module = generation_module
        self.tool_manager = tool_manager
        self.chat_history = []  # List of tuples: (user_question, assistant_answer)

    def reset_history(self):
        """Resets the conversation history."""
        self.chat_history = []

    async def process_query(self, user_question: str) -> str:
        """
        Main pipeline:
        1. Check if tool call is needed.
        2. If tool, execute and get result.
        3. If ontology query is needed.
        4. Parse results.
        5. Generate final answer using context and chat history.
        6. Update chat history.
        """
        logger.info(f"Processing query: {user_question}")
        context_info = ""
        
        # 1. Tool Call Decision
        tool_decision = await self.generation_module.decide_tool_call(
            user_question, 
            self.tool_manager.get_tool_descriptions()
        )
        
        if tool_decision:
            tool_name = tool_decision.get("tool_name")
            tool_args = tool_decision.get("args", {})
            try:
                tool_result = self.tool_manager.call_tool(tool_name, **tool_args)
                context_info += f"\n[工具调用结果 ({tool_name})]: {tool_result}\n"
            except Exception as e:
                context_info += f"\n[工具调用失败]: {e}\n"

        # 2. Ontology Query (Simplified for MVP)
        try:
            # Fetch all Person and Task entities as context (limit to reasonable amount in real app)
            persons = self.query_module.query_by_type("Person")
            tasks = self.query_module.query_by_type("Task")
            
            raw_results = persons[:5] + tasks[:5] # Limit context
            parsed_results = ResultParsingModule.parse_query_results(raw_results)
        except Exception as e:
            logger.error(f"Ontology query failed: {e}")
            parsed_results = "查询知识库时发生错误。"

        # 3. Generate Answer
        final_answer = await self.generation_module.generate_answer(
            user_question,
            parsed_results,
            context_info,
            chat_history=list(self.chat_history)
        )
        
        # 4. Update History
        self.chat_history.append((user_question, final_answer))
        
        return final_answer
