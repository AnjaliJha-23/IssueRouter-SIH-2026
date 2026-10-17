import json
import os

from dotenv import load_dotenv

from pipeline import nvidia_llm
from pipeline.config import SUMMARIZATION_MODEL

# Search and load .env from backend directory and workspace root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# Summarization provider:
#   nvidia      NVIDIA NIM chat completions (default; needs NVIDIA_API_KEY)
#   groq        legacy Groq SDK path, kept as a comparison fallback. The `groq`
#               package is optional and is not installed by requirements.txt.
#   extractive  deterministic first-150-char summary, no network at all
SUMMARIZATION_BACKEND = (os.getenv("SUMMARIZATION_BACKEND") or "nvidia").strip().lower()

GROQ_DEFAULT_MODEL = "groq/compound-mini"

_groq_client = None


def active_model() -> str:
    """Effective summarization model name, for audit records."""
    if SUMMARIZATION_BACKEND == "groq":
        return os.getenv("GROQ_MODEL", GROQ_DEFAULT_MODEL)
    return os.getenv("NVIDIA_MODEL", SUMMARIZATION_MODEL)


def _groq_client_or_none():
    global _groq_client
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    if _groq_client is None:
        try:
            from groq import Groq
            _groq_client = Groq(api_key=api_key)
        except Exception as e:
            print(f"[summarization] Groq client init notice: {e}. Using extractive fallback.")
            _groq_client = False
    return _groq_client if _groq_client is not False else None


def _call_nvidia(prompt: str) -> str:
    return nvidia_llm.chat(
        messages=[{"role": "user", "content": prompt}],
        model=active_model(),
        max_tokens=150,
        temperature=0.1,
    )


def _call_groq(prompt: str) -> str:
    client = _groq_client_or_none()
    if client is None:
        raise RuntimeError("GROQ_API_KEY is not set")
    response = client.chat.completions.create(
        model=active_model(),
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return response.choices[0].message.content


def _parse_summary_json(content: str) -> dict | None:
    """Parse the model's JSON reply, tolerating ```json ... ``` wrapping."""
    content = (content or "").strip()
    if content.startswith("```"):
        parts = content.split("```")
        if len(parts) < 2:
            return None
        content = parts[1]
        if content.startswith("json"):
            content = content[4:].strip()

    try:
        result = json.loads(content)
    except ValueError:
        return None

    if not isinstance(result, dict) or "title" not in result or "description" not in result:
        return None

    return {
        "title": str(result["title"]),
        "description": str(result["description"])
    }


def generate_summary(
    existing_summary: dict | None,
    new_evidence_text: str,
    domain: str,
    location: str
) -> dict:
    """
    Generates a canonical title and description for a Master Challenge.
    Returns: {"title": "...", "description": "...", "model": "<what served it>"}
    """
    # Deterministic Extractive Fallback
    fallback_desc = (new_evidence_text[:147] + "...") if len(new_evidence_text) > 150 else new_evidence_text
    fallback_title = f"{domain} Issue in {location}" if location else f"{domain} Issue"

    fallback_result = {
        "title": fallback_title,
        "description": fallback_desc,
        "model": "extractive"
    }

    if SUMMARIZATION_BACKEND == "extractive":
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
        if SUMMARIZATION_BACKEND == "groq":
            content = _call_groq(prompt)
        else:
            content = _call_nvidia(prompt)
    except Exception as e:
        print(f"[summarization] {SUMMARIZATION_BACKEND} call notice: {e}. Using extractive fallback.")
        return fallback_result

    parsed = _parse_summary_json(content)
    if parsed is None:
        print("[summarization] Model returned an unparsable summary. Using extractive fallback.")
        return fallback_result

    parsed["model"] = active_model()
    return parsed
