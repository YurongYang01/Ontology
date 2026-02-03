import asyncio
import logging
import sys
from ontology_tool.core.manager import OntologyManager
from .query_module import OntologyQueryModule
from .generation_module import AnswerGenerationModule
from .tool_manager import ToolManager
from .integration_module import AgentIntegrationModule
from .utils import setup_logging

logger = logging.getLogger(__name__)

async def run_interactive_session():
    # 1. Setup logging
    setup_logging()
    # Reduce logging verbosity for interactive session to avoid clutter
    logging.getLogger("agent_system").setLevel(logging.WARNING)
    logging.getLogger("ontology_tool").setLevel(logging.WARNING)

    print("\n" + "="*50)
    print("欢迎使用智能本体 Agent 问答系统")
    print("输入 'exit' 或 'quit' 退出系统")
    print("输入 'clear' 清除对话历史")
    print("="*50 + "\n")

    # 2. Initialize components
    manager = OntologyManager()
    query_module = OntologyQueryModule(manager)
    generation_module = AnswerGenerationModule()
    tool_manager = ToolManager()
    
    agent = AgentIntegrationModule(query_module, generation_module, tool_manager)

    while True:
        try:
            user_input = input("\n[用户]: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit"]:
                print("\n[系统]: 再见！")
                break
                
            if user_input.lower() == "clear":
                agent.reset_history()
                print("\n[系统]: 对话历史已清除。")
                continue

            print("[系统]: 正在思考...", end="\r")
            
            # Process query
            response = await agent.process_query(user_input)
            
            # Clear "thinking" line and print response
            sys.stdout.write("\033[K") # Clear line
            print(f"[Agent]: {response}")

        except KeyboardInterrupt:
            print("\n[系统]: 收到中断信号，正在退出...")
            break
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            print(f"\n[系统错误]: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_interactive_session())
    except Exception as e:
        logger.error(f"System failed: {e}")
