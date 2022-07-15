from .api import API as InternalAPI
import os

TWITTER_API = os.environ.get("TWITTER_WEB", "https://api.twitter.com")
Api = InternalAPI(api_url=TWITTER_API)
