import asyncio
import sys
import os

# Ensure the project root is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_system.main import run_interactive_session

if __name__ == "__main__":
    try:
        asyncio.run(run_interactive_session())
    except KeyboardInterrupt:
        pass
