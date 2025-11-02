from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session
from src.domain.models.feed import Feed, FeedItem, FeedItemRequest, FeedRequest, UpdateFeedRequest
from src.domain.ports.feeds_port import FeedsPort


class FeedsRepository(FeedsPort):

    def __init__(self, db: Session):
        self.db = db

    def create_feed(self, feed_request: FeedRequest) -> Feed:
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


    def update_feed(
            self,
            feed_id: int,
            update_feed_request: UpdateFeedRequest
    ) -> Feed:
        values = update_feed_request.model_dump(exclude_unset=True)
        values = {k: v for k, v in values.items() if v is not None}
        if not values:
            return self.get_feed_by_id(feed_id)

        set_clauses = ", ".join([f"{key} = :{key}" for key in values.keys()])
        sql = text(f"""
            UPDATE feeds
            SET {set_clauses}
            WHERE id = :id
            RETURNING id, external_id, name, created_at
        """)
        values["id"] = feed_id
        result = self.db.execute(sql, values).mappings().first()
        self.db.commit()

        if not result:
            raise ValueError(f"Feed with id {feed_id} not found")

        return Feed(
            id=result["id"],
            external_id=result["external_id"],
            name=result["name"],
            created_at=result["created_at"],
        )

    def delete_feed(self, feed_id: int) -> bool:
        sql = text("DELETE FROM feeds WHERE id = :id RETURNING id")
        result = self.db.execute(sql, {"id": feed_id}).first()
        self.db.commit()
        return result is not None

    def get_all_feeds(self) -> list[Feed]:
        sql = text("SELECT id, external_id, name, created_at FROM feeds")
        result = self.db.execute(sql)

        return [
            Feed(**item._mapping) for item in result
        ]

    def get_feed_by_external_id(self, external_id: UUID) -> Feed | None:
        sql = text(
            "SELECT id, name, external_id, created_at "
            "FROM feeds WHERE external_id = :external_id;"
        )
        result = self.db.execute(sql, {"external_id": external_id}).mappings().first()

        if result:
            return Feed(**result)
        return None

    def get_feed_by_id(self, id: int) -> Feed | None:
        sql = text(
            "SELECT id, name, external_id, created_at "
            "FROM feeds WHERE id = :id;"
        )
        result = self.db.execute(sql, {"id": id}).mappings().first()

        if result:
            return Feed(**result)
        return None

    def get_feed_items_by_feed_id(self, feed_id: int) -> list[FeedItem]:
        sql = text(
            "SELECT id, feed_id, external_id, link, title, description, author, created_at "
            "FROM feed_items WHERE feed_id = :feed_id;"
        )
        result = self.db.execute(
            sql,
            {"feed_id": feed_id}
        ).mappings()

        return [FeedItem(**feed_item) for feed_item in result]

    def create_feed_item(self, feed_item_request: FeedItemRequest) -> FeedItem:
        sql = text(
            "INSERT INTO feed_items (feed_id, link, title, description, author) "
            "VALUES (:feed_id, :link, :title, :description, :author) "
            "RETURNING id, feed_id, external_id, link, title, author, description, created_at"
        )
        result = self.db.execute(
            sql,
            {
                "feed_id": feed_item_request.feed_id,
                "link": feed_item_request.link,
                "title": feed_item_request.title,
                "description": feed_item_request.description,
                "author": feed_item_request.author
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
            author=data["author"]
        )

    def delete_feed_item(self, feed_item_id: int) -> bool:
        sql = text("DELETE FROM feed_items WHERE id = :id RETURNING id")
        result = self.db.execute(sql, {"id": feed_item_id}).first()
        self.db.commit()
        return result is not None
