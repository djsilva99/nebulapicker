def process_filters(
    picker_id: str,
    job_service
):
    job_service.process(int(picker_id))
