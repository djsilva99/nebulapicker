import ctypes
import gc


def process_filters(picker_id: str):
    try:
        from src.main import app
        app.state.job_service.process(int(picker_id))

    finally:
        gc.collect()
        try:
            libc = ctypes.CDLL("libc.so.6")
            libc.malloc_trim(0)
        except Exception:
            pass
