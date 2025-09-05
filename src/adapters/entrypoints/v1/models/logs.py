def format_log_message(type: str, subtype: str, message: str):
    return f"[{type}][{subtype}] {message}"


class APILog:
    REST_API = "REST API"
    WELCOME = "Welcome"

    WELCOME_SUCCESS = format_log_message(REST_API, WELCOME, "Success")
