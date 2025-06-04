import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompts import INSPECTION_PROMPT
from utils.ai_client import AIClient
from models.models import State, Item
import logging
import asyncio
import json



async def validate_content(llm: AIClient, item: Item) -> dict:
    """Validate a single item's content using the LLM."""
    try:
        messages = INSPECTION_PROMPT.format(
            content=item.cleaned_text,
            title=item.title,
            tags=item.content_tags,
            summary=item.summary,
            snippet=item.news_snippet
        )
        response = await llm.get_completion(messages)
        
        # Clean the response and parse JSON
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.endswith("```"):
            response = response[:-3]
        
        try:
            validation_result = json.loads(response)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON response: {response}")
            # Return a default validation result indicating failure
            return {
                "title_valid": False,
                "tags_valid": False,
                "summary_valid": False,
                "snippet_valid": False,
                "issues": {
                    "title": "Failed to validate due to parsing error",
                    "tags": "Failed to validate due to parsing error",
                    "summary": "Failed to validate due to parsing error",
                    "snippet": "Failed to validate due to parsing error"
                }
            }
        
        return validation_result
    except Exception as e:
        logging.error(f"Content validation failed: {e}")
        raise

async def reprocess_content(llm: AIClient, item: Item, issues: dict):
    """Reprocess content based on identified issues."""
    try:
        from agents.process import generate_title, generate_tags
        from agents.summarize import summarize_and_write
        
        if not issues['title_valid']:
            item.title = generate_title(llm, item.cleaned_text, item.source)
            
        if not issues['tags_valid']:
            item.content_tags = generate_tags(llm, item.cleaned_text, item.source)
            
        if not issues['summary_valid'] or not issues['snippet_valid']:
            temp_state = State(items=[item])
            temp_state = summarize_and_write(temp_state, llm)
            item.summary = temp_state.items[0].summary
            item.news_snippet = temp_state.items[0].news_snippet
            
    except Exception as e:
        logging.error(f"Content reprocessing failed: {e}")
        raise

def determine_next_step(validation_result: dict) -> str:
    """Determine which agent to redirect to based on validation results."""
    if not validation_result['title_valid'] or not validation_result['tags_valid']:
        return "process"
    elif not validation_result['summary_valid'] or not validation_result['snippet_valid']:
        return "summarize"
    return "continue"

def inspect_content(state: State, llm: AIClient) -> State:
    """Main inspection function that validates and fixes content if needed."""
    try:
        state.inspection_results = []  # Store validation results for each item
        needs_reprocessing = False
        
        for item in state.items:
            if not all([item.title, item.content_tags, item.summary, item.news_snippet]):
                continue
                
            # Validate content
            validation_result = asyncio.run(validate_content(llm, item))
            next_step = determine_next_step(validation_result)
            
            if next_step != "continue":
                needs_reprocessing = True
                # Store validation results and issues for the item
                state.inspection_results.append({
                    "item_id": item.id,
                    "next_step": next_step,
                    "issues": validation_result["issues"]
                })
                # Clear the fields that need to be regenerated
                if next_step == "process":
                    if not validation_result['title_valid']:
                        item.title = None
                    if not validation_result['tags_valid']:
                        item.content_tags = None
                elif next_step == "summarize":
                    if not validation_result['summary_valid']:
                        item.summary = None
                    if not validation_result['snippet_valid']:
                        item.news_snippet = None
                
        # Set the next step in the flow
        if needs_reprocessing:
            # Find the earliest step in the pipeline that needs fixing
            next_steps = [result["next_step"] for result in state.inspection_results]
            state.next_step = "process" if "process" in next_steps else "summarize"
            logging.info(f"Issues found. Redirecting to {state.next_step}")
            logging.info(f"Inspection results: {state.inspection_results}")
        else:
            state.next_step = "continue"
            logging.info("No issues found, continuing normal flow")
            
        return state
    except Exception as e:
        logging.error(f"Content inspection failed: {e}")
        raise

if __name__ == "__main__":
    from utils.ai_client import AIClient
    state = State()
    llm = AIClient()
    state = inspect_content(state, llm)
    print(state) 