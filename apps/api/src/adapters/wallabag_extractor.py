import requests
from ftfy import fix_text
from src.configs.settings import Settings
from src.domain.models.feed import FeedItemContent, GetFeedItemContentRequest
from src.domain.ports.extractor_port import ExtractorPort

settings: Settings = Settings()
MINIMUM_CONTENT_LEN = 200


class WallabagExtractor(ExtractorPort):
    def __init__(self):
        self.access_token = ""
        self.base_url = settings.WALLABAG_URL
        self.client_id = settings.WALLABAG_CLIENT_ID
        self.client_secret = settings.WALLABAG_CLIENT_SECRET
        self.username = settings.WALLABAG_USERNAME
        self.password = settings.WALLABAG_PASSWORD

    def get_feed_item_content(self,
        feed_item_content_request: GetFeedItemContentRequest
    ) -> FeedItemContent | None:

        try:
            token_url = f"{self.base_url}/oauth/v2/token"

            # Get token
            payload = {
                "grant_type": "password",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.username,
                "password": self.password
            }

            response = requests.post(token_url, data=payload, timeout=10)
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data.get("access_token")

            # Create and get wallabag entry
            entry_url = feed_item_content_request.url
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            payload = {
                "url": entry_url,
            }
            response = requests.post(
                f"{self.base_url}/api/entries",
                headers=headers,
                data=payload,
                timeout=15,
            )
            entry_data = response.json()
            try:
                title = fix_text(entry_data["title"])
            except Exception:
                title = entry_data["title"]
            if len(entry_data["content"]) < MINIMUM_CONTENT_LEN:
                content = "<p> Nebulapicker was not able to parse the content. </p>"
                reading_time = 0
            else:
                try:
                    content = fix_text(entry_data["content"])
                except Exception:
                    content = entry_data["content"]
                reading_time = entry_data.get("reading_time")

            # Remove wallabag entry
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            requests.delete(
                f"{self.base_url}/api/entries/{entry_data['id']}",
                headers=headers,
                timeout=15,
            )

            return FeedItemContent(
                title=title,
                content=content,
                reading_time=reading_time
            )
        except Exception:
            return None
