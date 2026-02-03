import os
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AnswerGenerationModule:
    """
    Module for generating answers using LLM based on query results and context.
    """
    def __init__(self, model_name="deepseek-chat"):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = "https://api.deepseek.com" # Default DeepSeek URL
        
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            openai_api_base=base_url,
            temperature=0
        )
        self.output_parser = StrOutputParser()

    async def generate_answer(self, question: str, parsed_results: str, context: str = "", chat_history: list = None) -> str:
        """
        Generates an answer based on the question, parsed query results, and context.
        """
        logger.info(f"Generating answer for question: {question}")
        
        chat_history_str = ""
        if chat_history:
            chat_history_str = "\n".join([f"User: {q}\nAssistant: {a}" for q, a in chat_history])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个智能问答助手。请根据提供的[查询结果]和[上下文]信息，准确、连贯地回答用户的问题。如果查询结果中没有相关信息，请诚实说明。同时，请参考之前的对话历史进行连贯的回答。"),
            ("user", "问题: {question}\n\n[对话历史]\n{chat_history}\n\n[查询结果]\n{results}\n\n[上下文]\n{context}")
        ])
        
        chain = prompt | self.llm | self.output_parser
        
        try:
            response = await chain.ainvoke({
                "question": question,
                "results": parsed_results,
                "context": context,
                "chat_history": chat_history_str
            })
            return response
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"抱歉，在生成回答时遇到了错误：{str(e)}"

    async def decide_tool_call(self, question: str, tool_descriptions: str) -> dict | None:
        """
        Decides if a tool needs to be called based on the question.
        Returns a dict with 'tool_name' and 'args' if a tool is needed, else None.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"你是一个决策助手。根据用户的问题，判断是否需要调用以下工具之一。如果需要，请返回 JSON 格式：{{{{'tool_name': '工具名', 'args': {{'参数名': '值'}}}}}}。如果不需要，请返回 'NONE'。\n\n可用工具：\n{tool_descriptions}"),
            ("user", "问题: {question}")
        ])
        
        chain = prompt | self.llm | self.output_parser
        
        try:
            response = await chain.ainvoke({"question": question})
            if response.strip().upper() == "NONE":
                return None
            
            # Simple JSON extraction (more robust logic could be added)
            import json
            import re
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                return json.loads(match.group())
            return None
        except Exception as e:
            logger.error(f"Error deciding tool call: {e}")
            return None
