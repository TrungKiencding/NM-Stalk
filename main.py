import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langgraph.graph import StateGraph
from models.models import State, Item
from agents.crawl import crawl_data
from agents.process import process_and_tag
from agents.summarize import summarize_and_write
from agents.inspect import inspect_content
from agents.synthesize import synthesize_articles
from agents.present import present_output
from utils.ai_client import AIClient
from models.database import Database
from config import Config
import logging

def after_inspect(state: State) -> str:
    """Determine next step after inspection."""
    if state.next_step == "process":
        return "process"
    elif state.next_step == "summarize":
        return "summarize"
    return "synthesize" if state.session_count % Config.SYNTHESIZE_INTERVAL == 0 else "present"

def main():
    try:
        db = Database()
        llm = AIClient()

        graph = StateGraph(State)
        graph.add_node("crawl", crawl_data)
        graph.add_node("process", lambda state: process_and_tag(state, llm))
        graph.add_node("summarize", lambda state: summarize_and_write(state, llm))
        graph.add_node("inspect", lambda state: inspect_content(state, llm))
        graph.add_node("synthesize", lambda state: synthesize_articles(state, db, llm))
        graph.add_node("present", present_output)

        # Set up the flow
        graph.add_edge("crawl", "process")
        graph.add_edge("process", "summarize")
        graph.add_edge("summarize", "inspect")
        
        # Add edges from inspect node
        graph.add_conditional_edges(
            "inspect",
            after_inspect,
            {
                "process": "process",
                "summarize": "summarize",
                "synthesize": "synthesize",
                "present": "present"
            }
        )
        
        graph.add_edge("synthesize", "present")
        graph.set_entry_point("crawl")

        app = graph.compile()

        initial_state = State(session_count=1)
        final_state = app.invoke(initial_state)
        if final_state and isinstance(final_state, dict) and 'items' in final_state:
            items_to_save = [Item(**item) if isinstance(item, dict) else item for item in final_state['items']]
            db.save_items(items_to_save)
            logging.info("Execution completed successfully")
        else:
            logging.warning("No items to save in final state")
    except Exception as e:
        logging.error(f"Main execution failed: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()