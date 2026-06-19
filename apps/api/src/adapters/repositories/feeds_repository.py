import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from src.domain.models.feed import Feed, FeedItem, FeedItemRequest, FeedRequest, UpdateFeedRequest
from src.domain.ports.feeds_port import FeedsPort

MAX_NUMBER_OF_ITEMS_IN_RSS = 50
MAX_NUMBER_OF_ITEMS = 250


class FeedsRepository(FeedsPort):

    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    def create_feed(self, feed_request: FeedRequest) -> Feed:
        sql = text(
            "INSERT INTO feeds (name) "
            "VALUES (:name) "
            "RETURNING id, name, external_id, created_at, updated_at"
        )
        with self.session_factory() as session:
            result = session.execute(
                sql,
                {"name": feed_request.name}
            ).first()
            session.commit()
            data = result._mapping
            return Feed(
                id=data["id"],
                name=data["name"],
                external_id=data["external_id"],
                created_at=data["created_at"],
                updated_at=data["updated_at"]
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
            RETURNING id, external_id, name, created_at, updated_at
        """)
        values["id"] = feed_id

        with self.session_factory() as session:
            result = session.execute(sql, values).mappings().first()
            session.commit()

            if not result:
                raise ValueError(f"Feed with id {feed_id} not found")

            return Feed(
                id=result["id"],
                external_id=result["external_id"],
                name=result["name"],
                created_at=result["created_at"],
                updated_at=result["updated_at"]
            )

    def delete_feed(self, feed_id: int) -> bool:
        sql = text("DELETE FROM feeds WHERE id = :id RETURNING id")
        with self.session_factory() as session:
            result = session.execute(sql, {"id": feed_id}).first()
            session.commit()
            return result is not None

    def get_all_feeds(self) -> list[Feed]:
        sql = text("SELECT id, external_id, name, created_at, updated_at FROM feeds")
        with self.session_factory() as session:
            result = session.execute(sql)
            return [Feed(**item._mapping) for item in result]

    def get_feed_by_external_id(self, external_id: UUID) -> Feed | None:
        sql = text(
            "SELECT id, name, external_id, created_at, updated_at "
            "FROM feeds WHERE external_id = :external_id;"
        )
        with self.session_factory() as session:
            result = session.execute(sql, {"external_id": external_id}).mappings().first()
            return Feed(**result) if result else None

    def get_feed_by_id(self, id: int) -> Feed | None:
        sql = text(
            "SELECT id, name, external_id, created_at, updated_at "
            "FROM feeds WHERE id = :id;"
        )
        with self.session_factory() as session:
            result = session.execute(sql, {"id": id}).mappings().first()
            return Feed(**result) if result else None

    def get_all_feed_items_by_feed_id(self, feed_id: int) -> list[FeedItem]:
        sql = text(
            "SELECT id, feed_id, external_id, link, title, description, author, created_at, "
            "content, reading_time, image_url "
            "FROM feed_items WHERE feed_id = :feed_id "
            "ORDER BY created_at DESC;"
        )
        with self.session_factory() as session:
            result = session.execute(sql, {"feed_id": feed_id}).mappings()
            return [FeedItem(**feed_item) for feed_item in result]

    def get_active_feed_items_by_feed_id(
            self,
            feed_id: int,
            title_search: str = "",
            limit: int | None = 20,
            offset: int = 0,
            last_day: bool = False,
            rss_items: bool = False,
    ) -> list[FeedItem]:

        title_search = title_search if title_search else None

        where_clauses = [
            "feed_id = :feed_id",
            "is_active = TRUE",
        ]

        params = {
            "feed_id": feed_id,
            "offset": offset,
            "title_search": title_search,
            "title_pattern": f"%{title_search}%" if title_search else None,
        }

        # optional filters (no OR in SQL anymore)
        if title_search:
            where_clauses.append("title ILIKE :title_pattern")

        if last_day:
            where_clauses.append("""
                created_at >= CASE
                    WHEN CURRENT_TIME < TIME '03:00:00'
                        THEN DATE_TRUNC('day', NOW()) - INTERVAL '1 day'
                    ELSE
                        DATE_TRUNC('day', NOW())
                END
                AND created_at <= NOW()
            """)

        sql = f"""
            SELECT id, feed_id, external_id, link, title, description, author, created_at,
                   reading_time, image_url, content
            FROM feed_items
            WHERE {' AND '.join(where_clauses)}
            ORDER BY created_at DESC
        """

        # pagination (optional)
        if limit is not None:
            if rss_items :
                max_offset = int(MAX_NUMBER_OF_ITEMS_IN_RSS / limit) * limit

                if offset == max_offset:
                    limit = (
                            MAX_NUMBER_OF_ITEMS_IN_RSS
                            - int(MAX_NUMBER_OF_ITEMS_IN_RSS / limit) * limit
                    )

            sql += " LIMIT :limit OFFSET :offset"
            params["limit"] = limit

        params["offset"] = offset if limit is not None else 0

        with self.session_factory() as session:
            result = session.execute(text(sql), params).mappings()
            return [FeedItem(**row) for row in result]

    def count_active_feed_items_by_feed_id(
            self,
            feed_id: int,
            title_search: str | None = None,
            last_day: bool = False,
    ) -> int:
        title_search = title_search if title_search else None

        where_clauses = [
            "feed_id = :feed_id",
            "is_active = TRUE",
        ]

        params = {
            "feed_id": feed_id,
            "title_search": title_search,
            "title_pattern": f"%{title_search}%" if title_search else None,
        }

        if title_search:
            where_clauses.append("title ILIKE :title_pattern")

        if last_day:
            where_clauses.append("""
                created_at >= CASE
                    WHEN CURRENT_TIME < TIME '03:00:00'
                        THEN DATE_TRUNC('day', NOW()) - INTERVAL '1 day'
                    ELSE
                        DATE_TRUNC('day', NOW())
                END
                AND created_at <= NOW()
            """)

        sql = text(f"""
            SELECT COUNT(*)
            FROM feed_items
            WHERE {' AND '.join(where_clauses)}
        """)

        with self.session_factory() as session:
            return session.execute(sql, params).scalar_one()

    def get_feed_item_by_feed_item_external_id(
            self,
            feed_item_external_id: UUID
    ) -> FeedItem | None:
        sql = text(
            "SELECT id, feed_id, external_id, link, title, description, author, created_at, "
            "content, reading_time "
            "FROM feed_items WHERE external_id = :external_id;"
        )
        with self.session_factory() as session:
            result = session.execute(
                sql,
                {
                    "external_id": feed_item_external_id
                }
            ).mappings().first()
            return FeedItem(**result) if result else None

    def create_feed_item(self, feed_item_request: FeedItemRequest) -> FeedItem:
        if feed_item_request.created_at is None:
            feed_item_request.created_at = datetime.datetime.now()
        sql = text(
            "INSERT INTO feed_items (feed_id, link, title, description, author, content, "
            "reading_time, created_at, image_url) "
            "VALUES (:feed_id, :link, :title, :description, :author, :content, "
            ":reading_time, :created_at, :image_url) "
            "RETURNING id, feed_id, external_id, link, title, author, description, content, "
            "reading_time, created_at, image_url"
        )
        with self.session_factory() as session:
            result = session.execute(
                sql,
                {
                    "feed_id": feed_item_request.feed_id,
                    "link": feed_item_request.link,
                    "title": feed_item_request.title,
                    "description": feed_item_request.description,
                    "author": feed_item_request.author,
                    "content": feed_item_request.content,
                    "reading_time": feed_item_request.reading_time,
                    "created_at": feed_item_request.created_at,
                    "image_url": feed_item_request.image_url
                }
            ).first()
            session.commit()
            data = result._mapping
            return FeedItem(
                id=data["id"],
                feed_id=data["feed_id"],
                external_id=data["external_id"],
                link=data["link"],
                title=data["title"],
                description=data["description"],
                author=data["author"],
                content=data["content"],
                reading_time=data["reading_time"],
                created_at=data["created_at"],
                image_url=data["image_url"]
            )

    def delete_feed_item(self, feed_item_id: int) -> bool:
        sql = text("DELETE FROM feed_items WHERE id = :id RETURNING id")
        with self.session_factory() as session:
            result = session.execute(sql, {"id": feed_item_id}).first()
            session.commit()
            return result is not None

    def get_number_of_feed_items_by_feed_id(self, feed_id: int):
        sql = text("""
            SELECT COUNT(*)
            FROM feed_items
            WHERE feed_id = :feed_id AND is_active = true;
        """)
        with self.session_factory() as session:
            return session.execute(sql, {"feed_id": feed_id}).scalar()

    def set_feed_item_as_inactive(self, feed_item_id: int):
        sql = text(
            "UPDATE feed_items "
            "SET is_active = FALSE "
            "WHERE id = :id "
            "RETURNING id"
        )
        with self.session_factory() as session:
            result = session.execute(sql, {"id": feed_item_id}).first()
            session.commit()
            return result is not None

    def set_updated_at(self, feed_id: int) -> bool:
        sql = text(
            "UPDATE feeds "
            "SET updated_at = CURRENT_TIMESTAMP "
            "WHERE id = :id "
            "RETURNING updated_at"
        )
        with self.session_factory() as session:
            result = session.execute(sql, {"id": feed_id}).first()
            session.commit()
            return result is not None
