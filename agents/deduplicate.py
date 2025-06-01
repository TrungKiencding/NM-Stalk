import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sklearn.metrics.pairwise import cosine_similarity
from models.models import State
import logging

SOURCE_PRIORITY = {"arXiv": 1, "GitHub": 2, "X": 3}

def deduplicate_and_select(state: State) -> State:
    try:
        '''
        candidates = [item for item in state.items if item.news_snippet is not None]
        if not candidates:
            logging.info("No candidates for deduplication")
            return state

        threshold = 0.8
        groups = []
        for i, item1 in enumerate(candidates):
            for j in range(i+1, len(candidates)):
                item2 = candidates[j]
                sim = cosine_similarity([item1.embedding], [item2.embedding])[0][0]
                if sim > threshold:
                    found = False
                    for group in groups:
                        if item1 in group or item2 in group:
                            group.add(item1)
                            group.add(item2)
                            found = True
                            break
                    if not found:
                        groups.append(set([item1, item2]))

        selected = set()
        for group in groups:
            best_item = min(group, key=lambda x: SOURCE_PRIORITY.get(x.source, 999))
            selected.add(best_item)
            for item in group - {best_item}:
                item.is_final_selection = False

        all_in_groups = set().union(*groups)
        for item in candidates:
            if item not in all_in_groups:
                selected.add(item)
                item.is_final_selection = True

        for item in state.items:
            item.is_final_selection = item in selected
        '''
        logging.info("Deduplication and selection completed")
        return state
    except Exception as e:
        logging.error(f"Deduplication failed: {e}")
        raise

if __name__ == "__main__":
    state = State()
    state = deduplicate_and_select(state)
    print(state)