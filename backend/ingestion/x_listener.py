"""
Real tweepy stream — post-hackathon swap.
Not used during demo. Swap stream_mock_tweets for stream_real_tweets
in main.py after the hackathon when you have an X developer account.
"""
import os

def stream_real_tweets(callback):
    try:
        import tweepy
    except ImportError:
        raise ImportError("Install tweepy: pip install tweepy")

    bearer_token = os.environ.get("X_BEARER_TOKEN")
    if not bearer_token:
        raise ValueError("X_BEARER_TOKEN not set in .env")

    class Handler(tweepy.StreamingClient):
        def on_tweet(self, tweet):
            callback({
                "id":         str(tweet.id),
                "username":   tweet.author_id,  # resolve to handle if needed
                "text":       tweet.text,
                "likes":      tweet.public_metrics.get("like_count", 0) if tweet.public_metrics else 0,
                "retweets":   tweet.public_metrics.get("retweet_count", 0) if tweet.public_metrics else 0,
                "created_at": str(tweet.created_at),
            })

        def on_error(self, status):
            print(f"[x_listener] Stream error: {status}")

    handler = Handler(bearer_token=bearer_token)

    # Clear old rules first
    existing = handler.get_rules()
    if existing.data:
        handler.delete_rules([r.id for r in existing.data])

    # Add hashtag filter
    handler.add_rules(tweepy.StreamRule("#complaints_gov"))
    print("[x_listener] Listening for #complaints_gov on X...")
    handler.filter(tweet_fields=["public_metrics", "created_at", "author_id"])