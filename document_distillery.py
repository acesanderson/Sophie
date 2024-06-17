from Chain import Chain, Prompt, Model, Parser, Response
from obsidian import summarize_text

example_urls = """
https://promptengineering.org/exploring-agentic-wagentic-workflows-the-power-of-ai-agent-collaborationorkflows-the-power-of-ai-agent-collaboration/
https://arxiv.org/html/2406.05804v1
https://masterdai.blog/exploring-agentic-workflows-a-deep-dive-into-ai-enhanced-productivity/
https://aws.amazon.com/blogs/hpc/building-an-ai-simulation-assistant-with-agentic-workflows/
https://www.reddit.com/r/LocalLLaMA/comments/1chpt5f/mechanisms_and_abstractions_for_building_agents/
""".strip().split("\n")

distill_prompt = """
Look at the following document(s).

We want the following documents condensed down to their essence, within one document. The goal is to have a summary
that is as short as possible but conveying as rich a context as is possible.
As such, focus each section summary on what is the most information dense bit of detail; avoid redundant informatio
(for example: if the corporate mission statement is "help companies upskill their employees", you do not need to
mention it in the "unique value proposition" section.)

Your response should be a series of document summaries, each starting with a header that has the name of the document.
Do not add any extra text -- this document should only be a collection of summaries.

{% for doc in documents %}
##################### 
{{ doc }}
#####################
{{ doc.summary }}
{% endfor %}
""".strip()

def summarize_docs(docs: list[str], research_question = "", persona = "", use_case = ""):
    """
    Summarize a list of documents.
    You can customize system prompt by providing a research question:
    "What is the best way to structure prompts for agentic workflows? Either tool-based or collaboration-based."
    By providing a persona:
    "You are a librarian with a phd in machine learning, and you have a deep understanding of 
    """
    summaries = []
    for doc in docs:
        title, summary = summarize_text(doc)
        summaries.append({"title": title, "summary": summary})
    return summaries

def concatenate_docs(docs: list[str]):
    """Combine docs into one string."""
    concatenated_doc: str
    for doc in docs:
        concatenated_doc += f"### {doc}\n"
    return concatenated_doc

