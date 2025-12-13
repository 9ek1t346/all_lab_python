import logging

from lab7.logger import logger
from lab7.currencies import get_currencies


def setup_file_logger() -> logging.Logger:
    file_logger = logging.getLogger("currency_file")
    file_logger.setLevel(logging.INFO)

    handler = logging.FileHandler("currency.log", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)

    # чтобы не добавлять обработчик повторно при повторных запусках
    if not file_logger.handlers:
        file_logger.addHandler(handler)

    return file_logger


def main() -> None:
    log = setup_file_logger()

    @logger(handle=log)
    def wrapped():
        return get_currencies(["USD"], url="https://www.cbr-xml-daily.ru/daily_json.js")

    print(wrapped())


if __name__ == "__main__":
    main()
D