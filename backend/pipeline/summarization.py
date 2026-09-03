import os
import json
from groq import Groq

_client = None

def get_client():
    global _client
    if _client is None:
        try:
            # Assumes GROQ_API_KEY is in env
            _client = Groq()
        except Exception as e:
            print(f"[summarization] Groq client init failed: {e}")
    return _client

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
    client = get_client()
    
    # Deterministic Extractive Fallback
    fallback_desc = (new_evidence_text[:147] + "...") if len(new_evidence_text) > 150 else new_evidence_text
    fallback_title = f"{domain} Issue in {location}" if location else f"{domain} Issue"
    
    fallback_result = {
        "title": fallback_title,
        "description": fallback_desc
    }
    
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

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=150,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        
        if "title" not in result or "description" not in result:
            return fallback_result
            
        return {
            "title": str(result["title"]),
            "description": str(result["description"])
        }
    except Exception as e:
        print(f"[summarization] API/JSON error: {e}. Using fallback.")
        return fallback_result