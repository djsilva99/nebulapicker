import feedparser
from src.domain.handlers.operations import identity
from src.domain.models.feed import FeedItemRequest
from src.domain.models.filter import Operation
from src.domain.models.job import Job
from src.domain.models.picker import Picker
from src.domain.ports.scheduler_port import SchedulerPort
from src.domain.services.feed_service import FeedService
from src.domain.services.filter_service import FilterService
from src.domain.services.picker_service import PickerService
from src.domain.services.source_service import SourceService


class JobService:
    def __init__(
        self,
        scheduler: SchedulerPort,
        picker_service: PickerService,
        filter_service: FilterService,
        source_service: SourceService,
        feed_service: FeedService
    ):
        self.scheduler = scheduler
        self.picker_service = picker_service
        self.filter_service = filter_service
        self.source_service = source_service
        self.feed_service = feed_service

    def add_cronjob(self, picker: Picker):
        job = Job(
            func_name='process_filters',
            args=[str(picker.id), self],
            schedule=picker.cronjob
        )
        self.scheduler.add_job(job)

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

    def process(self, picker_id: int):
        picker = self.picker_service.get_picker_by_id(picker_id)
        filters = self.filter_service.get_filters_by_picker_id(picker_id)
        feed_items = self.feed_service.get_feed_items(picker.feed_id)
        source = self.source_service.get_source_by_id(picker.source_id)
        source_set = feedparser.parse(source.url)
        entries = source_set.entries
        new_entries = [
            entry for entry in entries
            if entry.link not in {item.link for item in feed_items}
        ]

        for entry in new_entries:
            to_add = True
            for filter in filters:

                # identity operation
                if filter.operation is Operation.identity:
                    to_add = identity(to_add)

            if to_add:
                feed_item_request = FeedItemRequest(
                    link=entry.link,
                    title=entry.title,
                    description=entry.description,
                    feed_id=picker.feed_id
                )
                self.feed_service.create_feed_item(feed_item_request)
