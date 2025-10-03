from __future__ import annotations
from typing import List, Sequence, Tuple
import unittest

def build_range_list(start: int, end: int) -> List[int]:
    """Вернуть список целых чисел от ``start`` до ``end`` включительно.
    """
    if end < start:
        return []
    return list(range(start, end + 1))

def guess_number(target: int, values: Sequence[int], method: str = "binary") -> Tuple[int, int]:
    """Угадать число в списке, используя линейный перебор или бинарный поиск.
    """
    if not values:
        raise ValueError("'values' должен быть непустым.")
    if len(set(values)) != len(values):
        raise ValueError("'values' не должен содержать повторяющиеся элементы.")
    if target not in values:
        raise ValueError("Целевое число должно присутствовать в 'values'.")

    m = method.strip().lower()
    if m not in {"linear", "binary"}:
        raise ValueError("Неизвестный метод. Используйте 'linear' или 'binary'.")

    if m == "linear":
        # Линейный перебор: просто увеличиваем текущее предположение от минимума к максимуму.
        lo, hi = min(values), max(values)
        guesses = 0
        for x in range(lo, hi + 1):
            guesses += 1
            if x == target:
                return target, guesses
        raise RuntimeError("Цель не найдена линейным перебором.")

    # Бинарный поиск по отсортированной копии (исходный порядок не меняем).
    arr = sorted(values)
    left, right = 0, len(arr) - 1
    guesses = 0
    while left <= right:
        mid = (left + right) // 2
        guesses += 1
        if arr[mid] == target:
            return arr[mid], guesses
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    raise RuntimeError("Цель не найдена бинарным поиском.")

# Минимальные юнит‑тесты
class GuessNumberTests(unittest.TestCase):
    def test_build_range_list(self) -> None:
        self.assertEqual(build_range_list(1, 5), [1, 2, 3, 4, 5])
        self.assertEqual(build_range_list(3, 2), [])

    def test_linear(self) -> None:
        values = build_range_list(1, 10)
        target = 7
        found, guesses = guess_number(target, values, method="linear")
        self.assertEqual(found, target)
        # Для непрерывного диапазона количество попыток = target - min + 1
        self.assertEqual(guesses, target - min(values) + 1)

    def test_binary_unsorted(self) -> None:
        values = list(reversed(build_range_list(1, 20)))  # намеренно не сортируем
        target = 3
        found, guesses = guess_number(target, values, method="binary")
        self.assertEqual(found, target)
        # Для 20 элементов бинарный поиск укладывается в 5 сравнений.
        self.assertLessEqual(guesses, 5)

    def test_string_method_case_insensitive(self) -> None:
        values = build_range_list(1, 100)
        target = 42
        self.assertEqual(guess_number(target, values, method="BINARY")[0], target)
        self.assertEqual(guess_number(target, values, method="linear")[0], target)

    def test_invalid_inputs(self) -> None:
        with self.assertRaises(ValueError):
            guess_number(1, [], method="binary")
        with self.assertRaises(ValueError):
            guess_number(1, [1, 1, 2], method="binary")
        with self.assertRaises(ValueError):
            guess_number(0, build_range_list(1, 10), method="binary")
        with self.assertRaises(ValueError):
            guess_number(1, [1], method="fast")

if __name__ == "__main__":
    unittest.main()
