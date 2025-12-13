from lab7.logger import logger
from lab7.currencies import get_currencies


@logger  # по умолчанию sys.stdout
def run():
    return get_currencies(["USD", "EUR"], url="http://test")


if __name__ == "__main__":
    try:
        print(run())
    except Exception as exc:
        print("Поймали исключение:", type(exc).__name__, exc)
