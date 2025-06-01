import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_client import AIClient
from models.models import State
from prompts import SUMMARY_PROMPT, NEWS_SNIPPET_PROMPT
import logging
import asyncio

def summarize_and_write(state: State, llm: AIClient) -> State:
    try:
        for item in state.items:
            if item.is_novel and item.summary is None:
                messages = SUMMARY_PROMPT.format(content=item.cleaned_text)
                summary_response = asyncio.run(llm.get_completion(messages))
                item.summary = summary_response

                tags = ", ".join(item.content_tags + item.source_tags)
                messages = NEWS_SNIPPET_PROMPT.format(tags=tags, content=item.cleaned_text)
                snippet_response = asyncio.run(llm.get_completion(messages))
                item.news_snippet = snippet_response
        logging.info("Summarization and news writing completed")
        return state
    except Exception as e:
        logging.error(f"Summarization failed: {e}")
        raise

if __name__ == "__main__":
    state = State()
    llm = AIClient()
    state = summarize_and_write(state, llm)
    print(state)