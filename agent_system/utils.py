import logging
import sys

def setup_logging():
    """
    Configures logging for the agent system.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("agent_system.log")
        ]
    )
    # Set levels for some verbose libraries
    logging.getLogger("rdflib").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
