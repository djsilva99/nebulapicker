from datetime import datetime

def print_hello(name: str):
    now = datetime.utcnow()
    print(f"[{now}] Hello {name}!")
