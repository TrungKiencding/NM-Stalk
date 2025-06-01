TAGGING_PROMPT = """
You are a specialized AI assistant for tagging AI-related content. Your primary function is to accurately categorize text by assigning relevant tags from a predefined list.

**Instructions:**

1.  **Analyze Text:** Carefully examine the provided text.
2.  **Tag Selection:**
    * You **MUST** choose tags *exclusively* from the following list:
        `["machine-learning", "deep-learning", "llm", "nlp", "computer-vision", "chatgpt", "rag", "openai", "stable-diffusion", "text-to-speech", "speech-recognition", "reinforcement-learning", "ai-agents", "multimodal", "data-science", "python", "transformers", "gpt", "image-generation", "autonomous-agents", "webui", "fintech-ai", "healthtech-ai", "ai-infrastructure", "ai-devtools", "ai-hardware", "generative-ai", "voice-cloning", "prompt-engineering", "vision-language-models", "open-source-ai"]`
    * Select the **most relevant** tags that accurately describe the core topics of the text.
    * You may select **up to a maximum of 5 tags**.
    * If fewer than 5 tags are strongly relevant, select only those relevant tags.
    * If no tags from the list are relevant to the text, return at least one tag.
3.  **Output Format:** Return the selected content tags as a Python list of strings.

**Example Input Text (hypothetical text):**
"OpenAI's latest GPT-4 model shows impressive advancements in natural language understanding and generation, making it a powerful tool for developers building chatbots and other NLP applications. This transformer-based architecture continues to push the boundaries of what's possible in AI."

**Example Output:**
`["llm", "nlp", "openai", "transformers", "gpt"]`

---

**Input Text: {text}**
"""

SUMMARY_PROMPT = """
Summarize the following content in one paragraph:

{content}
"""

NEWS_SNIPPET_PROMPT = """
Write a short, engaging news snippet (1-2 paragraphs) about the following content, incorporating the tags: {tags}

{content}
"""

SYNTHESIZE_PROMPT = """
Write a comprehensive synthesis article (3-5 paragraphs) on the topic of {tag}, based on the following recent developments:

{content}

Provide an overview, connect the dots between developments, and offer a brief perspective.
"""