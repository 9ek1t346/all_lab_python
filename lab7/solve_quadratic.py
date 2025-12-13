"""
Демонстрация: решение квадратного уравнения.

Показывает разные уровни логирования через тип исключения:
- INFO: успешные расчёты,
- WARNING: дискриминант < 0,
- ERROR: неверные типы данных,
- CRITICAL: полностью невозможная ситуация (например a=b=0).
"""

from __future__ import annotations

import math
from typing import Tuple

from logger import LogLevelError, logger


class NegativeDiscriminant(LogLevelError, ValueError):
    """Дискриминант отрицательный; логировать как WARNING."""

    log_level = "WARNING"


class ImpossibleQuadratic(LogLevelError, ValueError):
    """Невозможная ситуация (например a=b=0); логировать как CRITICAL."""

    log_level = "CRITICAL"


@logger
def solve_quadratic(a: float, b: float, c: float) -> Tuple[float, float]:
    """
    Решить квадратное уравнение ax^2 + bx + c = 0 в вещественных числах.

    Возвращает
    ----------
    tuple[float, float]
        Два вещественных корня.

    Исключения
    ----------
    TypeError
        Если коэффициенты не являются числами.
    NegativeDiscriminant
        Если дискриминант < 0 (должно логироваться как WARNING).
    ImpossibleQuadratic
        Если a=b=0 (должно логироваться как CRITICAL).
    ValueError
        Если a=0 (это уже не квадратное уравнение).
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)) or not isinstance(c, (int, float)):
        raise TypeError("Коэффициенты должны быть числами")

    if a == 0 and b == 0:
        raise ImpossibleQuadratic("Оба коэффициента a и b равны нулю")

    if a == 0:
        raise ValueError("Это не квадратное уравнение (a=0)")

    d = b * b - 4 * a * c
    if d < 0:
        raise NegativeDiscriminant(f"Дискриминант отрицательный: {d}")

    sqrt_d = math.sqrt(d)
    x1 = (-b - sqrt_d) / (2 * a)
    x2 = (-b + sqrt_d) / (2 * a)
    return x1, x2
