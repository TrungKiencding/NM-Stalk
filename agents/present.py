import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.models import State
import logging

def present_output(state: State) -> State:
    try:
        for item in state.items:
            print("\nFinal selections:")
            #if item.is_final_selection and item.news_snippet:
            if item.news_snippet:
                print(f"{item.news_snippet}")
        for article in state.synthesized_articles:
            print("\nSynthesized articles:")
            print(f"Article on {article.tag}:\n{article.article}\n")
        logging.info("Output presented")
        return state
    except Exception as e:
        logging.error(f"Output presentation failed: {e}")
        raise       

if __name__ == "__main__":
    state = State()
    state = present_output(state)
    print(state)