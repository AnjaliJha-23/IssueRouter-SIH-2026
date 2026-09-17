import os
import json
from dotenv import load_dotenv

# Search and load .env from backend directory and workspace root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

_client = None

def get_client():
    global _client
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    if _client is None:
        try:
            from groq import Groq
            _client = Groq(api_key=api_key)
        except Exception as e:
            print(f"[summarization] Groq client init notice: {e}. Using extractive fallback.")
            _client = False
    return _client if _client is not False else None

def generate_summary(
    existing_summary: dict | None,
    new_evidence_text: str,
    domain: str,
    location: str
) -> dict:
    """
    Generates a canonical title and description for a Master Challenge.
    Returns: {"title": "...", "description": "..."}
    """
    global _groq_enabled
    # Deterministic Extractive Fallback
    fallback_desc = (new_evidence_text[:147] + "...") if len(new_evidence_text) > 150 else new_evidence_text
    fallback_title = f"{domain} Issue in {location}" if location else f"{domain} Issue"
    
    fallback_result = {
        "title": fallback_title,
        "description": fallback_desc
    }
    
    client = get_client()
    if client is None:
        return fallback_result
        
    context = ""
    if existing_summary:
        context = f"Previous Title: {existing_summary.get('title')}\nPrevious Description: {existing_summary.get('description')}\n"
        
    prompt = f"""You are a civic grievance summarizer.
Update or create a canonical summary for this issue based on new evidence.
Respond ONLY with a valid JSON object containing exactly two keys: "title" (max 10 words) and "description" (max 30 words).

Domain: {domain}
Location: {location}
{context}
New Evidence: {new_evidence_text}
"""

    model_name = os.getenv("GROQ_MODEL", "groq/compound-mini")
    try:
        response = client.chat.completions.create(
            model=model_name,
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        # Clean potential markdown wrapping e.g. ```json ... ```
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:].strip()
        result = json.loads(content)
        
        if "title" not in result or "description" not in result:
            return fallback_result
            
        return {
            "title": str(result["title"]),
            "description": str(result["description"])
        }
    except Exception as e:
        print(f"[summarization] Groq call notice: {e}. Switching to extractive fallback.")
        _groq_enabled = False
        return fallback_result