import json
import time
import random
from pathlib import Path

TWEETS_PATH = Path(__file__).parent / "tweets.json"

def load_tweets() -> list:
    if not TWEETS_PATH.exists():
        raise FileNotFoundError(
            f"tweets.json not found at {TWEETS_PATH}. "
            "Ask Dev 4 to generate it or use the sample below."
        )
    return json.loads(TWEETS_PATH.read_text())

def stream_mock_tweets(callback, interval_seconds: int = 8):
    """
    Replays tweets from tweets.json one by one with a delay.
    Loops back to start after exhausting the list.
    callback = the function to call with each tweet dict.
    """
    tweets = load_tweets()
    print(f"[mock_feed] Loaded {len(tweets)} tweets. Streaming every {interval_seconds}s...")

    idx = 0
    while True:
        tweet = dict(tweets[idx % len(tweets)])  # copy to avoid mutation

        # Prevent dedup collision on loop by suffixing the id
        tweet["id"] = f"{tweet['id']}_{idx}"

        try:
            callback(tweet)
            print(f"[mock_feed] Processed tweet #{idx}: @{tweet.get('username')}")
        except Exception as e:
            print(f"[mock_feed] Error processing tweet #{idx}: {e}")

        idx += 1
        jitter = random.uniform(0, 2)
        time.sleep(interval_seconds + jitter)