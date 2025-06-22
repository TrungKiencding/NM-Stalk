TAGGING_PROMPT = """
You are a specialized AI assistant for tagging AI-related content. Your primary function is to accurately categorize text by assigning relevant tags from a predefined list.

**Instructions:**

1. **Analyze Text:** Carefully examine the provided text.
2. **Tag Selection:**
    * You **MUST** choose tags *exclusively* from the following list: {tags}
    * Select the **most relevant** tags that accurately describe the core topics of the text.
    * You may select **up to a maximum of 5 tags**.
    * If fewer than 5 tags are strongly relevant, select only those relevant tags.
    * If the text is not AI Technology related, return ["TECHNOLOGY"].
    * If the text is AI-related but no tags fit exactly, select the closest relevant tag(s).
    * Always return tags in UPPERCASE.
3. **Output Format:** Return the selected content tags as a strings (e.g., LLM, NLP, OPENAI).

**Example Input Text:**
"OpenAI's latest GPT-4 model shows impressive advancements in natural language understanding and generation, making it a powerful tool for developers building chatbots and other NLP applications. This transformer-based architecture continues to push the boundaries of what's possible in AI."

**Example Output:**
LLM, NLP, OPENAI, TRANSFORMERS, GPT

---

**Input Text: {text}**
"""

TITLE_PROMPT = """
You are a specialized AI assistant for generating titles. Your primary function is to generate a concise, one-sentence title that fully represents the core message and key details of the text.

**Task:**
Read the following content and generate a one-sentence title that best summarizes the core message and key details.

**Detailed requirements:**
1. The title must be clear, complete, and fully representative of the passage.
2. The title must be in {language}.
3. The title must be no more than 10 words.
4. Avoid unnecessary words or generic phrases.
5. Your response must include only the title and nothing else.
**Input Text:**
{text}
"""

SUMMARY_PROMPT = """
You are a specialized AI assistant for summarizing content. Your primary function is to accurately summarize text by creating a short paragraph that highlights the most important main idea of the text.

**Task:**
Summarize the following content into a short paragraph that is concise and highlights only the most important main idea of the text. Use clear and standard English. The output should be a single paragraph, without bullet points or listings.

**Detailed requirements:**

1. Focus only on the most prominent main idea; do not include minor details.

2. Maximum length: 1-2 sentences.

3. Language: {language}.

4. Output format: One single paragraph, no line breaks, no special characters or bullet points.

5. Do not add personal opinions, comments, or extra information.

6. Do not repeat or refer to the task instructions in your answer.

**Content to summarize:**
{text}
"""

NEWS_SNIPPET_PROMPT = """
You are an expert in writing short news articles.

Your task is to generate a concise news article in {language} based on the inputs provided below. The output must be in Markdown and include:
  • A level-1 title (the article headline)  
  • A bolded one-sentence summary  
  • A rewritten snippet (2-3 paragraphs) that faithfully covers the full content  
  • A tag that is relevant to the content

Inputs:     
  • title: {title}  
  • summary: {summary}   
  • Text: {text}  
  • tag: {tag}
Requirements:
  – The snippet must be newly written (not copied verbatim).  
  – Cover all key points from Text.  
  – Keep it concise (1–2 paragraphs).  
  - No need to rewrite the tag, the title and summary.
  - No need to translate the tag, the title and summary.
  - Remove the '[]' from the tag.
  - If the provided Text is a not good for writing a news article, return only word Trash
Example Output (Markdown):
# Qwen2.5-VL: A New Multimodal Open-Source Model
**Summary:** The Qwen2.5-VL repository on GitHub unveils an advanced vision-language model supporting image-text tasks.

**Snippet:**  
QwenLM's new Qwen2.5-VL package merges state-of-the-art vision and language capabilities into a single open-source framework. Designed for quick setup, it delivers top performance on benchmarks such as image captioning and visual question answering, and offers seamless access via Python APIs. With thorough documentation and step-by-step installation guides, developers can clone the repo, install dependencies, and start experimenting in minutes.


**Tag:** LLMs, Vision-Language Models, Open-Source Models, Multimodal Models, Computer Vision
"""


INSPECTION_PROMPT = """
You are an expert content inspector. Your task is to validate the quality and accuracy of AI-generated content.
Please analyze the following content and identify any issues with:
1. Title: Check if it accurately represents the content are matching with original content
2. Tags: Verify if they are relevant and appropriate
3. Summary: Ensure it captures the main points without hallucinations or inaccuracies
4. News Snippet: Confirm it faithfully represents the original content

Original Content: {content}
Generated Title: {title}
Generated Tags: {tags}
Generated Summary: {summary}
Generated News Snippet: {snippet}

**Respond with a JSON object in this format:**  
{{
    "title_valid": true,
    "tags_valid": true,
    "summary_valid": true,
    "snippet_valid": true,
    "issues": {{
        "title": null,
        "tags": null,
        "summary": null,
        "snippet": null
    }}
}}

Note: 
- For each field in "issues", provide a very short description of the problem if the corresponding *_valid field is false, otherwise leave it as null.
- If the Generated News Snippet is 'Trash'. Response with a normal json object with all fields are true, and all issues are null.
"""

SOCIAL_PROMPT = """
You are a social media analyst. Based on the following trending topic and related posts, write a comprehensive report.


TRENDING TOPIC:
- Topic ID: {topic_id}
- Cluster Size: {size} posts
- Keywords: {keywords_str}
- Sources: {sources_str}
- Average Confidence: {avg_probability:.3f}

RELATED POSTS:
{posts_content}

The output must be in Markdown and include:
  • A level-1 title (the report headline)  
  • Briefly identify the overarching topic of the discussion. 
  • A rewritten snippet (2-3 paragraphs) Summary of discussion:
    - What key points, facts, or questions were raised?
    - What information or solutions were shared?
  • Summary and Comments:
    - Summarize the most important findings from your analysis.
    - Make a statement about the general trend of the discussion or the implications that can be drawn.


Make the report professional, insightful, and actionable. Focus on the most important aspects and provide clear, concise analysis.
"""