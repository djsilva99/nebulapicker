import ast

import feedparser
from src.configs.settings import Settings
from src.domain.handlers.operations import (
    description_contains,
    description_does_not_contain,
    identity,
    link_contains,
    link_does_not_contain,
    title_contains,
    title_does_not_contain,
)
from src.domain.models.feed import (
    FeedItemRequest,
    GetFeedItemContentRequest,
    GetFeedItemImageUrlRequest,
)
from src.domain.models.filter import Operation
from src.domain.models.job import Job
from src.domain.models.picker import Picker
from src.domain.ports.scheduler_port import SchedulerPort
from src.domain.services.extractor_service import ExtractorService
from src.domain.services.feed_service import FeedService
from src.domain.services.filter_service import FilterService
from src.domain.services.picker_service import PickerService
from src.domain.services.source_service import SourceService

settings: Settings = Settings()


class JobService:
    def __init__(
        self,
        scheduler: SchedulerPort,
        picker_service: PickerService,
        filter_service: FilterService,
        source_service: SourceService,
        feed_service: FeedService,
        extractor_service: ExtractorService
    ):
        self.scheduler = scheduler
        self.picker_service = picker_service
        self.filter_service = filter_service
        self.source_service = source_service
        self.feed_service = feed_service
        self.extractor_service = extractor_service

    def add_cronjob(self, picker: Picker):
        job = Job(
            func_name='process_filters',
            args=[str(picker.id), self],
            schedule=picker.cronjob
        )
        self.scheduler.add_job(job)

    def delete_cronjob(self, picker: Picker):
        job_to_delete = Job(
            func_name='process_filters',
            args=[str(picker.id), self],
            schedule=picker.cronjob
        )
        self.scheduler.delete_job(job_to_delete)

    def load_all(self):
        pickers = self.picker_service.get_all_pickers()
        jobs = []
        for picker in pickers:
            job = Job(
                func_name='process_filters',
                args=[str(picker.id), self],
                schedule=picker.cronjob
            )
            jobs.append(job)
        self.scheduler.load_jobs(jobs)

    def process(self, picker_id: int):  # noqa: C901
        picker = self.picker_service.get_picker_by_id(picker_id)
        filters = self.filter_service.get_filters_by_picker_id(picker_id)
        feed_items = self.feed_service.get_feed_items(picker.feed_id)
        source = self.source_service.get_source_by_id(picker.source_id)
        source_name = source.name if source.name else ""
        source_set = feedparser.parse(source.url)
        entries = source_set.entries
        new_entries = [
            entry for entry in entries
            if entry.link not in {item.link for item in feed_items}
        ]

        for entry in new_entries:
            description = entry.description
            if entry.get("tags"):
                tags = [tag['term'] for tag in entry.get("tags")]
                description += " ["
                for tag in tags:
                    description += "category: " + tag + "; "
                description = description[:-1] + "]"
            to_add = True
            for filter in filters:
                args = ast.literal_eval(filter.args)

                # identity operation
                if filter.operation is Operation.identity:
                    to_add = identity(to_add)

                # title_contains operation
                if filter.operation is Operation.title_contains:
                    to_add = title_contains(
                        to_add,
                        entry.title,
                        args[0],
                        int(args[1])
                    )

                # description_contains operation
                if filter.operation is Operation.description_contains:
                    to_add = description_contains(
                        to_add,
                        description,
                        args[0],
                        int(args[1])
                    )

                # title_does_not_contain operation
                if filter.operation is Operation.title_does_not_contain:
                    to_add = title_does_not_contain(
                        to_add,
                        entry.title,
                        args[0],
                        int(args[1])
                    )

                # description_does_not_contain operation
                if filter.operation is Operation.description_does_not_contain:
                    to_add = description_does_not_contain(
                        to_add,
                        description,
                        args[0],
                        int(args[1])
                    )

                # link_contains operation
                if filter.operation is Operation.link_contains:
                    to_add = link_contains(
                        to_add,
                        entry.link,
                        args[0],
                        int(args[1])
                    )

                # link_does_not_contain operation
                if filter.operation is Operation.link_does_not_contain:
                    to_add = link_does_not_contain(
                        to_add,
                        entry.link,
                        args[0],
                        int(args[1])
                    )

            if to_add:
                # this condition makes sure that feed_items are not duplicated
                # when processing pickers
                if not self.feed_service.get_feed_items(
                    feed_id=picker.feed_id,
                    title=entry.title
                ):
                    content = None
                    image_url = None
                    if settings.WALLABAG_ENABLED:
                        content = self.extractor_service.extract_feed_item_content(
                            GetFeedItemContentRequest(
                                url=entry.link
                            )
                        )
                        image_url = self.extractor_service.extract_feed_item_image(
                            GetFeedItemImageUrlRequest(
                                url=entry.link
                            )
                        )
                    if content:
                        reading_time = content.reading_time
                        content = content.content
                    else:
                        content = "<p> Nebulapicker was not able to parse the content. </p>"
                        reading_time = 0
                    feed_item_request = FeedItemRequest(
                        link=entry.link,
                        title=entry.title,
                        description=description,
                        feed_id=picker.feed_id,
                        author=source_name,
                        content=content,
                        reading_time=reading_time,
                        image_url=image_url
                    )
                    self.feed_service.create_feed_item(feed_item_request)
