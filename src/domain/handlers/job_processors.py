from src.domain.services.job_service import JobService


def process_filters(
    picker_id: str,
    job_service: JobService
):
    job_service.process(int(picker_id))
