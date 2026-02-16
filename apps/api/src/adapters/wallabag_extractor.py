import html

import requests
from ftfy import fix_text
from src.configs.settings import Settings
from src.domain.models.feed import (
    FeedItemContent,
    FeedItemImageUrl,
    GetFeedItemContentRequest,
    GetFeedItemImageUrlRequest,
)
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
            entry_data = self._get_entry_data(feed_item_content_request.url)
            try:
                title = fix_text(entry_data["title"])
            except Exception:
                title = entry_data["title"]
            if entry_data["preview_picture"]:
                image_url = entry_data["preview_picture"]
            else:
                image_url = None
            if len(entry_data["content"]) < MINIMUM_CONTENT_LEN:
                content = "<p> Nebulapicker was not able to parse the content. </p>"
                reading_time = 0
            else:
                try:
                    content = fix_text(entry_data["content"])
                    content = html.unescape(content)
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
                reading_time=reading_time,
                image_url=image_url
            )
        except Exception:
            return None

    def get_feed_item_image(
        self,
        get_feed_item_image_url_request: GetFeedItemImageUrlRequest
    ) -> FeedItemImageUrl | None:
        try:
            entry_data = self._get_entry_data(get_feed_item_image_url_request.url)
            return entry_data["preview_picture"]

        except Exception:
            return None

    def _get_entry_data(self, url):
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
        entry_url = url
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
        return response.json()
