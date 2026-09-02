import re

def clean_text(raw: str) -> str:
    """
    Strips hashtags, @mentions, URLs, extra whitespace from raw tweet text.
    Returns clean text ready for NLP pipeline.
    """
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', raw)
    # Remove @mentions
    text = re.sub(r'@\w+', '', text)
    # Remove hashtags (keep the word, remove the #)
    text = re.sub(r'#(\w+)', r'\1', text)
    # Remove special characters except basic punctuation
    text = re.sub(r'[^\w\s\.,!?-]', '', text)
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text