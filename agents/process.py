import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_client import AIClient
from models.models import State
from prompts import TAGGING_PROMPT, TITLE_PROMPT
import re
from config import Config
import logging
from datetime import datetime
import asyncio
import json

def clean_text(text: str) -> str:
    """
    Clean text while preserving meaningful structure and punctuation
    """
    try:
        if not text or not isinstance(text, str):
            raise ValueError("Input must be a non-empty string")
            
        # Replace multiple spaces, newlines, and tabs with single space
        cleaned = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        cleaned = re.sub(r'[^\w\s.,!?-]', '', cleaned)
        
        # Remove extra spaces around punctuation
        cleaned = re.sub(r'\s+([.,!?-])', r'\1', cleaned)
        
        # Normalize to single spaces and trim
        cleaned = ' '.join(cleaned.split())
        
        if not cleaned.strip():
            raise ValueError("Cleaning resulted in empty string")
            
        logging.info("Text cleaned successfully")
        return cleaned
    except Exception as e:
        logging.error(f"Text cleaning failed: {e}")
        raise

def generate_tags(llm: AIClient, text: str, source: str) -> tuple[list[str], list[str]]:
    try:
        messages = TAGGING_PROMPT.format(text=text, tags=Config.ai_tags)

        # Run async function in synchronous context
        response = asyncio.run(llm.get_completion(messages))
        content = response  
        # Clean and parse tags
        content_tags = [tag.strip() for tag in content.strip().split(",") if tag.strip()]
        logging.info(f"Generated tags for {source}: {content_tags}")
        return content_tags
    except Exception as e:
        logging.error(f"Tag generation failed: {e}")
        raise

def generate_title(llm: AIClient, text: str, source: str) -> str:
    try:
        messages = TITLE_PROMPT.format(text=text, language=Config.LANGUAGE)
        response = asyncio.run(llm.get_completion(messages))
        title = response
        logging.info(f"Generated title for {source}: {title}")
        return title
    except Exception as e:
        logging.error(f"Title generation failed: {e}")
        raise

def process_and_tag(state: State, llm: AIClient) -> State:
    try:
        for item in state.items:
            if item.cleaned_text is None:
                item.cleaned_text = clean_text(item.content_snippet)
                item.content_tags = generate_tags(llm, item.cleaned_text, item.source)
                if item.title is None:
                    item.title = generate_title(llm, item.cleaned_text, item.source)
                logging.info("Generated title")
                # Run async function in synchronous context
                logging.info(f"Generating embedding for title")
                embedding = asyncio.run(llm.get_embedding(item.title))
                # Convert numpy float32 to regular Python list
                item.embedding = [float(x) for x in embedding]
        logging.info("Processed and tagged items")
        return state
    except Exception as e:
        logging.error(f"Process and tag failed: {e}")
        raise
