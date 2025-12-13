"""
Сравнение времени построения бинарного дерева: рекурсивный и итеративный подходы.

Модуль строит полное бинарное дерево двумя способами (рекурсивно и итеративно),
замеряет их производительность с помощью :mod:`timeit` и строит график результатов.

Условия задачи:

* Значение в корне дерева (root) задаётся пользователем.
* Высота дерева (height) задаётся пользователем.
* Для каждой вершины со значением ``v`` значения потомков вычисляются так:
    левый  = v + v // 2
    правый = v ** 2
"""

from __future__ import annotations

import timeit
from typing import Any, Dict, Tuple, Callable, Iterable, List

import matplotlib.pyplot as plt

#базовые псевдонимы типов


Tree = Dict[str, Any]
"""Узел бинарного дерева, представленный в виде вложенного словаря.

Каждый узел содержит следующие ключи:
    - "value": int         — значение, хранящееся в узле;
    - "left":  Tree | None — левое поддерево или None (для листа);
    - "right": Tree | None — правое поддерево или None (для листа).
"""


#вспомогательные функции


def child_values(value: int) -> Tuple[int, int]:
    """Вычислить значения левого и правого потомков узла.

    В соответствии с индивидуальным заданием:

        левый_потомок  = value + value // 2
        правый_потомок = value ** 2

    Args:
        value: Значение, хранящееся в текущем узле.

    Returns:
        Пара (left, right) — значения левого и правого потомков.
    """
    left = value + value // 2
    right = value ** 2
    return left, right


#построение дерева


def build_tree_recursive(data: Tuple[int, int]) -> Tree:
    """Построить полное бинарное дерево рекурсивным способом.

    Дерево:

    * имеет значение корня ``data[0]``;
    * имеет высоту ``data[1]`` уровней (height >= 1);
    * для каждого узла со значением ``v`` значения потомков задаются
      функцией :func:`child_values`.

    Представление дерева:
        Вложенный словарь с ключами "value", "left" и "right". У листьев
        оба поля "left" и "right" равны None.

    Args:
        data: Кортеж (root, height), где:
            root:   начальное значение в корне дерева;
            height: высота дерева (количество уровней, >= 1).

    Returns:
        Корневой узел построенного дерева.

    Raises:
        ValueError: Если height меньше 1.
    """
    root, height = data

    if height < 1:
        raise ValueError("height must be >= 1")

    def _build(value: int, level: int) -> Tree:
        """Рекурсивно построить поддерево с заданным корневым значением.

        Args:
            value: Значение, которое записывается в текущий узел.
            level: Текущий уровень (1 для корня).

        Returns:
            Поддерево с корнем в текущем узле.
        """
        if level >= height:
            return {"value": value, "left": None, "right": None}

        left_value, right_value = child_values(value)
        return {
            "value": value,
            "left": _build(left_value, level + 1),
            "right": _build(right_value, level + 1),
        }

    return _build(root, 1)


def build_tree_iterative(data: Tuple[int, int]) -> Tree:
    """Построить полное бинарное дерево итеративным способом (без рекурсии).

    Эта функция строит то же самое дерево, что и
    :func:`build_tree_recursive`, но вместо рекурсии использует явный
    стек и цикл.

    Args:
        data: Кортеж (root, height), где:
            root:   начальное значение в корне дерева;
            height: высота дерева (количество уровней, >= 1).

    Returns:
        Корневой узел построенного дерева.

    Raises:
        ValueError: Если height меньше 1.
    """
    root_value, height = data

    if height < 1:
        raise ValueError("height must be >= 1")

    root: Tree = {"value": root_value, "left": None, "right": None}
    stack: List[Tuple[Tree, int]] = [(root, 1)]

    while stack:
        node, level = stack.pop()

        if level >= height:
            continue

        value = node["value"]
        left_value, right_value = child_values(value)

        left_node: Tree = {"value": left_value, "left": None, "right": None}
        right_node: Tree = {"value": right_value, "left": None, "right": None}

        node["left"] = left_node
        node["right"] = right_node

        stack.append((right_node, level + 1))
        stack.append((left_node, level + 1))

    return root


#бенчмарк и построение графика


def benchmark(
    func: Callable[[Tuple[int, int]], Tree],
    root: int,
    heights: Iterable[int],
    number: int = 1_000,
) -> List[float]:
    """Измерить время построения деревьев разной высоты.

    Args:
        func:    Функция построения дерева, которую требуется измерить.
        root:    Значение в корне, используемое во всех экспериментах.
        heights: Набор высот дерева, которые нужно протестировать.
        number:  Сколько раз вызвать ``func`` для каждой высоты.

    Returns:
        Список времён (в секундах). i-й элемент соответствует высоте
        ``heights[i]`` и содержит суммарное время всех ``number`` вызовов.
    """
    times: List[float] = []

    for h in heights:
        data = (root, h)
        timer = timeit.Timer(lambda: func(data))
        elapsed = timer.timeit(number=number)
        times.append(elapsed)

    return times


def main() -> None:
    """Запустить бенчмарк и построить график результатов.

    Используются следующие значения:

        root   = 8   (согласно индивидуальному заданию);
        height = 1..10;
        number = 1000 повторов для каждой высоты.

    В консоль выводятся «сырые» результаты замеров, а затем показывается
    график, где по оси X откладывается высота дерева, а по оси Y —
    суммарное время построения дерева указанное число раз.
    """
    root = 8
    heights = list(range(1, 11))  # высоты от 1 до 10
    repeats = 1_000

    recursive_times = benchmark(build_tree_recursive, root, heights, repeats)
    iterative_times = benchmark(build_tree_iterative, root, heights, repeats)

    print("Результаты бенчмарка (суммарное время в секундах):")
    for h, t_rec, t_iter in zip(heights, recursive_times, iterative_times):
        print(
            f"height={h:2d}: "
            f"recursive={t_rec:.6f} s, "
            f"iterative={t_iter:.6f} s"
        )

    # Построение графика
    plt.figure()
    plt.plot(heights, recursive_times, marker="o", label="рекурсивный")
    plt.plot(heights, iterative_times, marker="s", label="итеративный")
    plt.xlabel("Высота дерева (количество уровней)")
    plt.ylabel(f"Суммарное время для {repeats} запусков, секунды")
    plt.title("Построение бинарного дерева: рекурсия vs итерация")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
