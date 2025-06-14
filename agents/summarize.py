import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_client import AIClient
from models.models import State
from prompts import SUMMARY_PROMPT, NEWS_SNIPPET_PROMPT
import logging
import asyncio
from config import Config

def summarize_and_write(state: State, llm: AIClient) -> State:
    try:
        for item in state.items:
            if  item.summary is None:
                messages = SUMMARY_PROMPT.format(text=item.cleaned_text, language=Config.LANGUAGE)
                summary_response = asyncio.run(llm.get_completion(messages))
                item.summary = summary_response

                messages = NEWS_SNIPPET_PROMPT.format(text=item.cleaned_text, summary=item.summary, title=item.title, url=item.url, language=Config.LANGUAGE, tag=item.content_tags)
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