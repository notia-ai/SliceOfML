import requests
from typing import Optional
from .display import Display
from datetime import datetime, timedelta


class API:
    """
    Class representing the twitter API
    """

    def __init__(self, user_agent: str, bearer_token: str, api_url: str) -> None:
        self._session = requests.Session()
        self._api_url = api_url
        self._request_url = self._api_url + "/2/tweets/search/recent"
        self._page_size = 100
        self._max_pages = 100
        self._user_agent = user_agent
        self._bearer_token = bearer_token
        self._display = Display()

    def bearer_oauth(self, r):
        """
        Method required by bearer token authentication.
        """
        r.headers["Authorization"] = f"Bearer {self._bearer_token}"
        r.headers["User-Agent"] = self._user_agent
        return r

    def query(self, frequency: str):
        try:
            page = 0
            next_token = ""
            user_map = {}
            tweets = []

            while page < self._max_pages and next_token is not None:
                response = self._get_request(self._build_url(next_token, frequency))
                json = response.json()
                next_token = json["meta"].get("next_token")
                for user in json["includes"]["users"]:
                    user_map[user["id"]] = user["username"]
                for tweet in json["data"]:
                    tweets.append(
                        (
                            tweet["id"],
                            tweet["text"],
                            tweet["public_metrics"]["like_count"],
                            user_map.get(tweet["author_id"]),
                        )
                    )
                page += 1

            return tweets
        except requests.exceptions.RequestException:
            self._display.error(
                (
                    "Failed to fetch search results, please ensure you "
                    "you have your API keys configured correctly."
                )
            )
        except Exception as err:
            self._display.error(f"{err}")

    def _build_url(self, next_token: Optional[str], frequency: str) -> str:
        query_url = (
            f"{self._request_url}?query=context:66.898661583827615744&"
            f"tweet.fields=public_metrics&max_results={self._page_size}&expansions=author_id"
        )
        if next_token and len(next_token) > 1:
            query_url = f"{query_url}&next_token={next_token}"
        if frequency == "daily":
            timestamp = datetime.utcnow() + timedelta(days=-1)
            query_url = f"{query_url}&start_time={timestamp.isoformat('T')}Z"
        return query_url

    def _get_request(self, url: str) -> requests.Response:
        return self._session.get(url, auth=self.bearer_oauth)
