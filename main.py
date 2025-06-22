import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langgraph.graph import StateGraph
from models.models import State, Item
from agents.research import crawl_data
from agents.process import process_and_tag
from agents.summarize import summarize_and_write
from agents.inspector import inspect_content
from agents.filter import filter_output
from agents.social import analyze_social_trends
from utils.ai_client import AIClient
from models.database import Database
from config import Config
import logging
from typing import Dict, Any, Optional

db = Database()
llm = AIClient()

def after_inspect(state: State) -> str:
    """Determine next step after inspection."""
    valid_steps = {"crawl", "process", "summarize", "filter", "social"}
    next_step = state.next_step or "filter"
    
    if next_step == "continue":
        return "filter"  # If no issues found, proceed to filter
    
    if next_step not in valid_steps:
        logging.warning(f"Invalid next step '{next_step}', defaulting to 'filter'")
        return "filter"
    
    return next_step

def save_state_to_db(db: Database, state: Dict[str, Any]) -> None:  
    """Save the final state to database."""
    if not state:
        logging.warning("No items to save in final state")
        return

    if 'items' in state:
        items_to_save = [Item(**item) if isinstance(item, dict) else item for item in state['items']]
        db.save_items(items_to_save)
        logging.info(f"Saved {len(items_to_save)} items to database")
    
    if 'hot_topics' in state:
        db.save_hot_topics(state['hot_topics'])
        logging.info(f"Saved hot topics to database")

def create_workflow_graph(llm: AIClient) -> StateGraph:
    """Create and configure the workflow graph."""
    graph = StateGraph(State)
    
    # Add nodes
    graph.add_node("crawl", crawl_data)
    graph.add_node("process", lambda state: process_and_tag(state, llm))
    graph.add_node("summarize", lambda state: summarize_and_write(state, llm))
    graph.add_node("inspect", lambda state: inspect_content(state, llm))
    graph.add_node("filter", lambda state: filter_output(state))
    graph.add_node("social", lambda state: analyze_social_trends(state, llm))

    # Set up the main flow
    graph.add_edge("crawl", "process")
    graph.add_edge("process", "summarize")
    graph.add_edge("summarize", "inspect")
    graph.add_edge("filter", "social")
    
    # Add conditional edges from inspect
    graph.add_conditional_edges(
        "inspect",
        after_inspect,
        {
            "process": "process",
            "summarize": "summarize",
            "filter": "filter",
            "social": "social"
        }
    )
    
    graph.set_entry_point("crawl")
    
    return graph

def main():
    try:

        # Create and compile workflow
        graph = create_workflow_graph(llm)
        app = graph.compile()

        # Initialize and run the workflow
        initial_state = State(session_count=1)
        final_state = app.invoke(initial_state, {"recursion_limit": 100})
        
        # Save results
        save_state_to_db(db, final_state)
        logging.info("Execution completed successfully")
            
    except Exception as e:
        logging.error(f"Main execution failed: {e}")
        raise
    finally:
        if db:
            db.session.close()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()