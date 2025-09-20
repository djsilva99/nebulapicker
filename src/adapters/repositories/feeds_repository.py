from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session
from src.domain.models.feed import Feed, FeedItem, FeedItemRequest, FeedRequest
from src.domain.ports.feeds_port import FeedsPort


class FeedsRepository(FeedsPort):

    def __init__(self, db: Session):
        self.db = db

    def create(self, feed_request: FeedRequest) -> Feed:
        sql = text(
            "INSERT INTO feeds (name) "
            "VALUES (:name) "
            "RETURNING id, name, external_id, created_at"
        )
        result = self.db.execute(
            sql,
            {"name": feed_request.name}
        ).first()

        self.db.commit()

        data = result._mapping
        return Feed(
            id=data["id"],
            name=data["name"],
            external_id=data["external_id"],
            created_at=data["created_at"],
        )

    def get_all(self) -> list[Feed]:
        sql = text("SELECT id, external_id, name, created_at FROM feeds")
        result = self.db.execute(sql)

        return [
            Feed(**item._mapping) for item in result
        ]

    def get_by_external_id(self, external_id: UUID) -> Feed | None:
        sql = text(
            "SELECT id, name, external_id, created_at "
            "FROM feeds WHERE external_id = :external_id;"
        )
        result = self.db.execute(sql, {"external_id": external_id}).mappings().first()

        if result:
            return Feed(**result)
        return None

    def get_by_id(self, id: int) -> Feed | None:
        sql = text(
            "SELECT id, name, external_id, created_at "
            "FROM feeds WHERE id = :id;"
        )
        result = self.db.execute(sql, {"id": id}).mappings().first()

        if result:
            return Feed(**result)
        return None

    def get_feed_items(self, feed_id: int) -> list[FeedItem]:
        sql = text(
            "SELECT id, feed_id, external_id, link, title, description, created_at "
            "FROM feed_items WHERE feed_id = :feed_id;"
        )
        result = self.db.execute(
            sql,
            {"feed_id": feed_id}
        ).mappings()

        return [FeedItem(**feed_item) for feed_item in result]

    def create_feed_item(self, feed_item_request: FeedItemRequest) -> FeedItem:
        sql = text(
            "INSERT INTO feed_items (feed_id, link, title, description) "
            "VALUES (:feed_id, :link, :title, :description) "
            "RETURNING id, feed_id, external_id, link, title, description, created_at"
        )
        result = self.db.execute(
            sql,
            {
                "feed_id": feed_item_request.feed_id,
                "link": feed_item_request.link,
                "title": feed_item_request.title,
                "description": feed_item_request.description
            }
        ).first()

        self.db.commit()

        data = result._mapping
        return FeedItem(
            id=data["id"],
            feed_id=data["feed_id"],
            external_id=data["external_id"],
            link=data["link"],
            title=data["title"],
            description=data["description"],
            created_at=data["created_at"],
        )
