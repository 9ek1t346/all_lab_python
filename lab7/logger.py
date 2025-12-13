"""
Декоратор логирования с поддержкой потоков вывода и logging.Logger.

Модуль предоставляет параметризуемый декоратор `logger`, который логирует
вызовы функций в один из вариантов:
- текстовый поток через `.write()` (например sys.stdout, io.StringIO),
- либо в `logging.Logger` через методы `.info()/.error()`.

Декоратор не изменяет сигнатуру оборачиваемой функции (используется
functools.wraps).
"""

from __future__ import annotations

import logging
import sys
from functools import wraps
from typing import Any, Callable, Optional, Protocol, TypeVar, overload

try:
    from typing import ParamSpec
except ImportError:
    from typing_extensions import ParamSpec


P = ParamSpec("P")
R = TypeVar("R")


class SupportsWrite(Protocol):
    """Протокол для объектов, поддерживающих `.write(str)` (интерфейс файла)."""

    def write(self, s: str) -> Any:
        """Записать строку в поток."""


class LogLevelError(Exception):
    """
    Базовое исключение, которое содержит желаемый уровень логирования.

    Если выброшенное исключение является экземпляром этого класса, декоратор
    может логировать его с уровнем `exc.log_level` (например WARNING/CRITICAL),
    а не всегда ERROR.
    """

    log_level: str = "ERROR"


def _emit(handle: Any, level: str, message: str) -> None:
    """
    Отправить сообщение лога в указанный обработчик.

    Если handle — это logging.Logger, используются методы логгера.
    Иначе предполагается поток/файл-подобный объект с методом `.write()`.
    """
    if isinstance(handle, logging.Logger):
        method = getattr(handle, level.lower(), handle.info)
        method(message)
        return

    line = f"{level}: {message}\n"
    handle.write(line)

    flush = getattr(handle, "flush", None)
    if callable(flush):
        flush()


@overload
def logger(func: Callable[P, R], *, handle: Any = sys.stdout) -> Callable[P, R]:
    ...


@overload
def logger(
    func: None = None, *, handle: Any = sys.stdout
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


def logger(
    func: Optional[Callable[P, R]] = None,
    *,
    handle: Any = sys.stdout,
) -> Any:
    """
    Параметризуемый декоратор для логирования вызовов функций.

    Параметры
    ---------
    func:
        Функция, которую нужно обернуть. При использовании как `@logger`
        передаётся автоматически. При использовании как `@logger(handle=...)`
        равен None, и возвращается функция-декоратор.
    handle:
        Куда писать логи:
        - logging.Logger -> логирование через .info()/.error() (и др. по уровню)
        - поток/файл-подобный объект -> логирование через .write()

    Возвращает
    ----------
    Callable
        Обёрнутую функцию (или декоратор при использовании с параметрами).
    """

    def decorator(target: Callable[P, R]) -> Callable[P, R]:
        @wraps(target)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            _emit(handle, "INFO", f"Старт {target.__name__} args={args} kwargs={kwargs}")
            try:
                result = target(*args, **kwargs)
            except Exception as exc:
                level = "ERROR"
                if isinstance(exc, LogLevelError):
                    level = getattr(exc, "log_level", "ERROR") or "ERROR"

                _emit(
                    handle,
                    level,
                    f"{target.__name__} выбросила {type(exc).__name__}: {exc}",
                )
                raise

            _emit(
                handle,
                "INFO",
                f"{target.__name__} успешно завершилась result={result!r}",
            )
            return result

        return wrapper

    if func is not None:
        return decorator(func)

    return decorator
