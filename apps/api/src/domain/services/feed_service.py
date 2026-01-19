import datetime
import imghdr
import io
from uuid import UUID

import requests
from bs4 import BeautifulSoup
from ebooklib import epub
from feedgenerator import Rss201rev2Feed
from src.adapters.entrypoints.v1.models.feeds import ExportFileType
from src.configs.settings import Settings
from src.domain.models.feed import (
    DetailedFeed,
    Feed,
    FeedItem,
    FeedItemRequest,
    FeedRequest,
    GetFeedItemContentRequest,
    UpdateFeedRequest,
)
from src.domain.ports.feeds_port import FeedsPort
from src.domain.services.extractor_service import ExtractorService

settings: Settings = Settings()

MAX_NUMBER_OF_ITEMS = 250
MAX_NUMBER_OF_ITEMS_IN_RSS = 50
HOURS_TO_COMPARE = 24


class FeedService:
    def __init__(self, feeds_port: FeedsPort, extractor_service: ExtractorService):
        self.feeds_port = feeds_port
        self.extractor_service = extractor_service

    def create_feed(self, feed_request: FeedRequest) -> Feed:
        return self.feeds_port.create_feed(feed_request)

    def update_feed(
        self,
        feed_external_id: UUID,
        update_feed_request: UpdateFeedRequest
    ) -> Feed:
        feed = self.get_feed_by_external_id(feed_external_id)
        if feed is None:
            return None
        return self.feeds_port.update_feed(feed.id, update_feed_request)

    def delete_feed(self, feed_id: int) -> bool:
        return self.feeds_port.delete_feed(feed_id)

    def get_feed_item_by_external_id(self, feed_item_external_id: UUID):
        return self.feeds_port.get_feed_item_by_feed_item_external_id(feed_item_external_id)

    def get_all_feeds(self) -> list[Feed]:
        return sorted(self.feeds_port.get_all_feeds(), key=lambda item: item.name)

    def get_detailed_feeds(self) -> list[DetailedFeed]:
        feeds = self.feeds_port.get_all_feeds()
        detailed_feeds = []
        for feed in feeds:
            feed_items = self.feeds_port.get_active_feed_items_by_feed_id(feed.id)
            number_of_feed_items = self.feeds_port.get_number_of_feed_items_by_feed_id(feed.id)
            latest_item_datetime = max((i.created_at for i in feed_items), default=feed.created_at)
            detailed_feeds.append(
                DetailedFeed(
                    id=feed.id,
                    external_id=feed.external_id,
                    name=feed.name,
                    created_at=feed.created_at,
                    latest_item_datetime=latest_item_datetime,
                    number_of_feed_items=number_of_feed_items,
                )
            )
        return sorted(detailed_feeds, key=lambda item: item.name)

    def get_feed_by_external_id(self, external_id: UUID) -> Feed | None:
        return self.feeds_port.get_feed_by_external_id(external_id)

    def get_feed_by_id(self, id: int) -> Feed | None:
        return self.feeds_port.get_feed_by_id(id)

    def get_feed_items(
        self,
        feed_id: int,
        title: str | None = None,
        all_items: bool = False
    ) -> list[FeedItem]:
        if all_items:
            feed_items = sorted(
                self.feeds_port.get_all_feed_items_by_feed_id(feed_id),
                key=lambda item: item.created_at
            )
        else:
            feed_items = sorted(
                self.feeds_port.get_active_feed_items_by_feed_id(feed_id),
                key=lambda item: item.created_at
            )
        if title:
            feeds_to_return = []
            for feed_item in feed_items:
                if (
                    feed_item.title == title and
                    feed_item.created_at >= (
                        datetime.datetime.now() - datetime.timedelta(hours=HOURS_TO_COMPARE)
                    )
                ):
                    feeds_to_return.append(feed_item)
            return feeds_to_return
        return feed_items

    def create_feed_item(self, feed_item_request: FeedItemRequest) -> FeedItem | None:
        if settings.WALLABAG_ENABLED:
            try:
                feed_item_data = self.extractor_service.extract_feed_item_content(
                    GetFeedItemContentRequest(
                        url=feed_item_request.link
                    )
                )
                feed_item_request.reading_time = feed_item_data.reading_time
                if feed_item_request.title == "":
                    feed_item_request.title = feed_item_data.title
                if feed_item_request.content == "":
                    feed_item_request.content = feed_item_data.content
                if feed_item_request.image_url == "":
                    feed_item_request.image_url = feed_item_data.image_url
                return self.feeds_port.create_feed_item(feed_item_request)
            except Exception:
                return None
        return self.feeds_port.create_feed_item(feed_item_request)

    def delete_feed_item(self, feed_item_id: int) -> bool:
        return self.feeds_port.delete_feed_item(feed_item_id)

    def deactivate_feed_item(self, feed_item_id: int) -> bool:
        return self.feeds_port.set_feed_item_as_inactive(feed_item_id)

    def get_rss(self, feed_external_id: UUID) -> str | None:
        feed = self.feeds_port.get_feed_by_external_id(feed_external_id)
        if not feed:
            return None
        feed_items = self.feeds_port.get_active_feed_items_by_feed_id(feed.id)
        feed_object = Rss201rev2Feed(
            title=feed.name,
            link="http://127.0.0.1:8080/" + str(feed.external_id),
            description=feed.name,
            language="en",
        )
        for feed_item in feed_items[:MAX_NUMBER_OF_ITEMS_IN_RSS]:
            feed_object.add_item(
                title=feed_item.title,
                link=feed_item.link,
                description=feed_item.description,
                author_name=feed_item.author,
                pubdate=feed_item.created_at
            )

        return feed_object.writeString("utf-8")

    def export_file(
        self,
        feed_external_id: UUID,
        file_type: ExportFileType,
        start_time: datetime,
        end_time: datetime
    ) -> io.BytesIO:
        # initialize buffer
        buffer = io.BytesIO()

        # Get feed items
        start_time = start_time.astimezone(datetime.UTC)
        end_time = end_time.astimezone(datetime.UTC)
        feed = self.feeds_port.get_feed_by_external_id(feed_external_id)
        feed_items = self.feeds_port.get_active_feed_items_by_feed_id(feed.id)
        feed_items_to_export = [
            item for item in feed_items if
            item.created_at.replace(
                tzinfo=datetime.UTC
            ) > start_time and
            item.created_at.replace(tzinfo=datetime.UTC) < end_time
        ]
        total_reading_time = sum(
            [item.reading_time for item in feed_items_to_export]
        )

        if file_type == ExportFileType.epub.value:

            # Create EPUB
            book = epub.EpubBook()
            book.set_identifier(str(feed.external_id))
            start_str = start_time.strftime("%Y%m%d")
            end_str = end_time.strftime("%Y%m%d")
            book.set_title(f"{feed.name}_{start_str}-{end_str} ({total_reading_time}m)")
            book.set_language("en")

            i = 0
            spine = ["nav"]
            toc = []
            for feed_item in feed_items_to_export:
                soup = BeautifulSoup(feed_item.content, "html.parser")

                for j, img_tag in enumerate(soup.find_all("img")):
                    img_url = img_tag.get("src")
                    if not img_url:
                        continue

                    try:
                        headers = {
                            "User-Agent": (
                                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                "(KHTML, like Gecko) Chrome/131 Safari/537.36"
                            )
                        }
                        resp = requests.get(img_url, headers=headers, timeout=10)
                        data = resp.content
                    except Exception:
                        continue  # skip download errors

                    # Detect actual image type (jpeg, png, gif, webp, etc.)
                    img_type = imghdr.what(None, data)

                    if img_type is None:
                        # Not an image (likely HTML)
                        continue

                    # Map imghdr types to EPUB media types
                    media_types = {
                        "jpeg": "image/jpeg",
                        "png": "image/png",
                        "gif": "image/gif",
                        "webp": "image/webp",
                        "bmp": "image/bmp",
                        "tiff": "image/tiff",
                    }

                    media_type = media_types.get(img_type)
                    if not media_type:
                        continue  # unsupported format

                    # Use correct extension
                    img_name = f"images/{i}_{j}.{img_type}"

                    epub_img = epub.EpubItem(
                        uid=f"img{i}_{j}",
                        file_name=img_name,
                        media_type=media_type,
                        content=data
                    )
                    book.add_item(epub_img)

                    # Update HTML <img src="...">
                    img_tag["src"] = img_name

                # Build chapter HTML
                chapter_html = f"""
                <!DOCTYPE html>
                <html lang="en">
                  <head>
                    <meta charset="utf-8"/>
                    <title>
                      {feed_item.created_at.strftime("%Y-%m-%d")}
                      - {feed_item.title} ({feed_item.reading_time}m)
                    </title>
                  </head>
                  <body>
                    <h1>{feed_item.title}</h1>
                    <div class="article-info">
                      <p>
                        <strong>
                          Reading time:
                        </strong>
                        {feed_item.reading_time}m
                      </p>
                      <p>
                        <strong>
                          Source:
                        </strong>
                        {feed_item.author}
                      </p>
                      <p>
                        <strong>
                          Date:
                        </strong>
                        {feed_item.created_at.strftime("%Y-%m-%d")}
                      </p>
                      <p>
                        <strong>
                          Link:
                        </strong>
                        <a href="{feed_item.link}">{feed_item.link}</a>
                      </p>
                    </div>
                    <div style="height: 24px;">&nbsp;</div>
                    <div style="height: 24px;">&nbsp;</div>
                    {str(soup)}
                  </body>
                </html>
                """

                chapter = epub.EpubHtml(
                    title=f"{feed_item.created_at.strftime('%Y-%m-%d')} - "
                          f"{feed_item.title} ({feed_item.reading_time}m)",
                    file_name=f"{i}.xhtml",
                    lang="en",
                )
                chapter.content = chapter_html
                book.add_item(chapter)
                spine.append(chapter)
                toc.append(chapter)
                i += 1

            # Update buffer
            book.spine = spine
            book.toc = toc
            book.add_item(epub.EpubNav())
            book.add_item(epub.EpubNcx())
            epub.write_epub(buffer, book, {})
            buffer.seek(0)

            return buffer

        raise Exception("wrong file type")
