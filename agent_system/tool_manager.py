import logging
import operator

logger = logging.getLogger(__name__)

class ToolManager:
    """
    Manager for external tools that can be called by the agent.
    """
    def __init__(self):
        self.tools = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """
        Registers some basic built-in tools.
        """
        self.register_tool("calculator", self._calculator, "计算数学表达式。参数: expression (str)")
        self.register_tool("knowledge_base_search", self._kb_placeholder, "搜索外部知识库。参数: query (str)")

    def register_tool(self, name: str, func: callable, description: str):
        """
        Registers a new tool.
        """
        self.tools[name] = {
            "func": func,
            "description": description
        }
        logger.info(f"Tool registered: {name}")

    def call_tool(self, name: str, **kwargs) -> any:
        """
        Calls a registered tool by name with arguments.
        """
        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")
        
        logger.info(f"Calling tool: {name} with args: {kwargs}")
        try:
            return self.tools[name]["func"](**kwargs)
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            raise

    def get_tool_descriptions(self) -> str:
        """
        Returns a string describing all available tools.
        """
        descriptions = []
        for name, info in self.tools.items():
            descriptions.append(f"- {name}: {info['description']}")
        return "\n".join(descriptions)

    def _calculator(self, expression: str) -> str:
        """
        Simple calculator tool.
        """
        # Safety check: only allow basic math characters
        allowed_chars = "0123456789+-*/(). "
        if not all(c in allowed_chars for c in expression):
            return "错误: 表达式包含非法字符。"
        
        try:
            # Note: eval is generally unsafe, but with the above check it's limited.
            # In a real system, use a proper math parser.
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"计算错误: {e}"

    def _kb_placeholder(self, query: str) -> str:
        """
        Placeholder for knowledge base search.
        """
        return f"针对 '{query}' 的外部知识库搜索结果（示例）。"
