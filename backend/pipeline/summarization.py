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
    fallback_desc = (
        new_evidence_text[:147] + "..."
        if len(new_evidence_text) > 150
        else new_evidence_text
    )

    fallback_title = (
        f"{domain} Issue in {location}"
        if location
        else f"{domain} Issue"
    )

    fallback_result = {
        "title": fallback_title,
        "description": fallback_desc
    }

    client = get_client()

    if client is None:
        print(
            "[summarization] Groq API key unavailable. "
            "Using extractive fallback."
        )
        return fallback_result

    context = ""

    if existing_summary:
        context = (
            f"Previous Title: {existing_summary.get('title', '')}\n"
            f"Previous Description: "
            f"{existing_summary.get('description', '')}\n"
        )

    prompt = f"""You are a civic grievance summarizer.

Create or update a concise canonical summary of a civic issue.

Return ONLY a valid JSON object with exactly these keys:
- "title": a concise title of at most 10 words
- "description": a description of at most 30 words

Do not include Markdown fences or any text outside the JSON object.

Domain: {domain}
Location: {location}

{context}

New Evidence:
{new_evidence_text}
"""

    # Use the model configured in Azure App Service.
    # The fallback is a current candidate, not a guarantee of availability.
    model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=200,
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        if not response.choices:
            print("[summarization] Groq returned no choices.")
            return fallback_result

        message = response.choices[0].message
        raw_content = message.content

        if not raw_content or not raw_content.strip():
            finish_reason = response.choices[0].finish_reason
            print(
                "[summarization] Groq returned empty content. "
                f"Finish reason: {finish_reason}"
            )
            return fallback_result

        content = raw_content.strip()

        # Remove Markdown fences if the response contains them.
        if content.startswith("```"):
            content = content.split("```", 2)[1].strip()

            if content.lower().startswith("json"):
                content = content[4:].strip()

        result = json.loads(content)

        if not isinstance(result, dict):
            print("[summarization] Model response was not a JSON object.")
            return fallback_result

        title = result.get("title")
        description = result.get("description")

        if not isinstance(title, str) or not title.strip():
            print("[summarization] Missing or invalid title.")
            return fallback_result

        if not isinstance(description, str) or not description.strip():
            print("[summarization] Missing or invalid description.")
            return fallback_result

        return {
            "title": title.strip(),
            "description": description.strip()
        }

    except Exception as e:
        # Log the error type and message, but never log the API key.
        print(
            f"[summarization] Groq summarization failed "
            f"({type(e).__name__}): {e}. "
            "Using extractive fallback."
        )
        return fallback_result