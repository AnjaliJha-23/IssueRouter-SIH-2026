import os
import json
from pathlib import Path
from groq import Groq

client = Groq()  # reads GROQ_API_KEY from .env automatically

# Cache path — fallback if API is down during demo
CACHE_PATH = Path(__file__).parent.parent / "cache" / "summaries.json"

def _load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text())
    return {}

def _save_cache(cache: dict):
    CACHE_PATH.write_text(json.dumps(cache, indent=2))

def summarise_cluster(
    cluster_id: str,
    aggregated_texts: list[str],
    location: str,
    category: str,
    complaint_count: int
) -> str:
    """
    Calls Groq (Llama 3.1) to generate a one-line officer brief for a cluster.
    Falls back to cache if API fails.
    Only recalculates at thresholds: 10, 50, 100, 250 complaints.
    """
    # Check cache first
    cache = _load_cache()
    cache_key = f"{cluster_id}_{complaint_count}"

    if cache_key in cache:
        return cache[cache_key]

    # Only regenerate at milestone counts
    THRESHOLDS = [1, 10, 50, 100, 250, 500]
    if complaint_count not in THRESHOLDS and cluster_id in cache:
        # Return last cached summary for this cluster
        last_key = [k for k in cache if k.startswith(cluster_id)]
        if last_key:
            return cache[sorted(last_key)[-1]]

    # Build context from sample tweets (max 5)
    sample = aggregated_texts[:5]
    combined = "\n".join(f"- {t}" for t in sample)

    prompt = f"""You are a civic grievance analyst briefing a District Magistrate.
Given the following citizen complaint cluster, write ONE sentence (maximum 25 words) for a government officer.
Be factual, location-specific, and actionable. No preamble. No quotes.

Category: {category}
Location: {location}
Total complaints: {complaint_count}
Sample complaints:
{combined}

Output only the brief sentence."""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        summary = response.choices[0].message.content.strip()

        # Cache the result
        cache[cache_key] = summary
        _save_cache(cache)

        return summary

    except Exception as e:
        print(f"[summariser] Groq API error: {e}. Falling back to cache.")

        # Fallback: return last known summary or generic one
        last = [v for k, v in cache.items() if k.startswith(cluster_id)]
        if last:
            return last[-1]

        return f"{complaint_count} complaints about {category.lower()} issues in {location}. Immediate review required."

def generate_recommended_action(
    category: str,
    location: str,
    urgency: str
) -> str:
    """
    Generates a recommended action string for the officer card.
    Uses Groq (Llama 3.1) for quality. Falls back to rule-based if API fails.
    """
    FALLBACK_ACTIONS = {
        "Infrastructure": f"Dispatch PWD inspection team to {location}. File urgent repair order.",
        "Sanitation":     f"Deploy MCD sanitation crew to {location}. Clear backlog within 24 hours.",
        "Healthcare":     f"Alert Health Dept for {location}. Send medical response team.",
        "Utilities":      f"Contact Jal Board / BSES for {location}. Restore service within 4 hours.",
        "Law and Order":  f"Notify local police station for {location}. Increase patrol frequency.",
        "Environment":    f"Raise alert with CPCB for {location}. Begin environmental assessment.",
        "Education":      f"Notify District Education Officer for {location}.",
    }

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=60,
            messages=[{
                "role": "user",
                "content": f"Write a 1-sentence recommended government action for a {urgency} urgency {category} complaint in {location}. Be specific and actionable. No preamble."
            }]
        )
        return response.choices[0].message.content.strip()

    except Exception:
        return FALLBACK_ACTIONS.get(category, f"Escalate {category} issue in {location} to relevant department immediately.")