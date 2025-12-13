import io

from lab7.logger import logger


def main() -> None:
    stream = io.StringIO()

    @logger(handle=stream)
    def test_function(x: int) -> int:
        return x * 2

    test_function(3)

    # Печатаем, что накопилось в stream
    print(stream.getvalue())


if __name__ == "__main__":
    main()
