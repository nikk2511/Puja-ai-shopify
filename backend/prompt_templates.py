"""
Prompt templates for the Puja AI chatbot system.
Contains system prompts and user prompt templates as specified.
"""

from typing import List, Dict, Any

# System prompt - EXACT as specified in requirements
SYSTEM_PROMPT = """You are an expert in Hindu puja and ritual guidance. You MUST ONLY use the information contained in the provided book excerpts below. Do not use any outside knowledge, personal assumptions, or web sources. If the provided excerpts don't contain the requested information, say "Not available in source books." Be precise, respectful, and organized.

Deliver outputs in this JSON format (no extra prose outside JSON):
{
  "summary": "<one-line summary>",
  "steps": [
    {"step_no": 1, "title": "Preparation", "instruction": "..." },
    ...
  ],
  "materials": [
    {"name": "<item name>", "description": "<optional>", "quantity": "<if available>", "product_match": "<shopify_product_handle_or_url or null>"}
  ],
  "timings": ["<e.g. morning, auspicious date>", ...],
  "mantras": ["<mantra text if available>"],
  "sources": [
    {"book": "<name>", "page": <page>, "snippet": "<short excerpt>"}
  ],
  "notes": "<caveats or disagreements between sources>"
}"""

# User prompt template
USER_PROMPT_TEMPLATE = """User asked: "{expanded_question}"

Below are the most relevant excerpts from the indexed books (use only these). Each excerpt includes metadata.

{retrieved_excerpts_formatted}

Answer the user's request strictly using only the above excerpts and the system instructions. Produce the JSON object exactly as specified."""

def format_retrieved_excerpts(retrieved_docs: List[Dict[str, Any]]) -> str:
    """
    Format retrieved documents into the prompt template format.
    
    Args:
        retrieved_docs: List of documents with 'page_content' and 'metadata' keys
        
    Returns:
        Formatted string with excerpts preceded by metadata headers
    """
    formatted_excerpts = []
    
    for doc in retrieved_docs:
        metadata = doc.get('metadata', {})
        page_content = doc.get('page_content', '')
        
        book_title = metadata.get('book_title', 'Unknown')
        page = metadata.get('page', 'Unknown')
        chunk_id = metadata.get('chunk_id', 'Unknown')
        
        header = f"--- Book: {book_title} | Page: {page} | Chunk: {chunk_id} ---"
        formatted_excerpts.append(f"{header}\n{page_content}")
    
    return "\n\n".join(formatted_excerpts)

def build_user_prompt(expanded_question: str, retrieved_docs: List[Dict[str, Any]]) -> str:
    """
    Build the complete user prompt with question and retrieved excerpts.
    
    Args:
        expanded_question: The user's question (expanded/rewritten)
        retrieved_docs: List of retrieved documents from ChromaDB
        
    Returns:
        Complete user prompt string
    """
    retrieved_excerpts_formatted = format_retrieved_excerpts(retrieved_docs)
    
    return USER_PROMPT_TEMPLATE.format(
        expanded_question=expanded_question,
        retrieved_excerpts_formatted=retrieved_excerpts_formatted
    )

def get_system_prompt() -> str:
    """Get the system prompt."""
    return SYSTEM_PROMPT

# Preset puja questions mapping
PRESET_QUESTIONS = {
    "ganesh": "Provide a step-by-step procedure for 'Ganesh Puja'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "durga": "Provide a step-by-step procedure for 'Durga Puja'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "lakshmi": "Provide a step-by-step procedure for 'Lakshmi Puja'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "saraswati": "Provide a step-by-step procedure for 'Saraswati Puja'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "shiva": "Provide a step-by-step procedure for 'Shiva Puja'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "vishnu": "Provide a step-by-step procedure for 'Vishnu Puja'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "krishna": "Provide a step-by-step procedure for 'Krishna Puja'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "hanuman": "Provide a step-by-step procedure for 'Hanuman Puja'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "kali": "Provide a step-by-step procedure for 'Kali Puja'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "ram": "Provide a step-by-step procedure for 'Ram Puja'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "ganesha_chaturthi": "Provide a step-by-step procedure for 'Ganesha Chaturthi celebration'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "diwali": "Provide a step-by-step procedure for 'Diwali Puja and celebration'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "navratri": "Provide a step-by-step procedure for 'Navratri Puja and celebration'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "holi": "Provide a step-by-step procedure for 'Holi celebration and rituals'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "janmashtami": "Provide a step-by-step procedure for 'Janmashtami celebration'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "general_home_puja": "Provide a step-by-step procedure for 'general daily home puja'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "morning_prayers": "Provide a step-by-step procedure for 'morning prayers and worship'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "evening_aarti": "Provide a step-by-step procedure for 'evening aarti'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "satyanarayan": "Provide a step-by-step procedure for 'Satyanarayan Puja'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books.",
    "griha_pravesh": "Provide a step-by-step procedure for 'Griha Pravesh (housewarming) ceremony'. Include: 1) A numbered step-by-step procedure 2) A bullet list of required materials with exact names 3) Any special timings or auspicious days 4) Mantras or short chants (if present in the sources) 5) Source citations (book name + page) for each major step or claim. Only use information from the indexed books."
}

def get_preset_questions() -> Dict[str, str]:
    """Get the preset questions mapping."""
    return PRESET_QUESTIONS
