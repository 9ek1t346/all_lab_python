# -*- coding: utf-8 -*-
"""Рекурсивный генератор бинарного дерева.

Вариант проверки:
- левый потомок:  left(x)  = x + x/2
- правый потомок: right(x) = x ** 2   (в Python оператор возведения в степень — **, а ^ — XOR)

Поддерживаемые контейнеры результата:
- "dict"       -> словарь с ключами {"value", "left", "right"}
- "list"       -> список вида [value, left, right]
- "dataclass"  -> dataclass Node
- "namedtuple" -> collections.namedtuple NodeNT
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Callable, Generic, Literal, Optional, TypeVar, Union
from collections import namedtuple

T = TypeVar("T", int, float)
ContainerName = Literal["dict", "list", "dataclass", "namedtuple"]


@dataclass
class Node(Generic[T]):
    """Узел бинарного дерева (вариант контейнера: dataclass).

    Attributes:
        value: Значение, хранящееся в узле.
        left:  Левый потомок (или None для листа).
        right: Правый потомок (или None для листа).
    """
    value: T
    left: Optional["Node[T]"] = None
    right: Optional["Node[T]"] = None


# Вариант контейнера из collections: namedtuple
NodeNT = namedtuple("NodeNT", "value left right")


def default_left(x: T) -> T:
    """Стандартная формула левого потомка: x + x/2."""
    return x + (x / 2)


def default_right(x: T) -> T:
    """Стандартная формула правого потомка: x ** 2."""
    return x ** 2


def gen_bin_tree(
    height: int,
    root: T,
    *,
    left_fn: Callable[[T], T] = default_left,
    right_fn: Callable[[T], T] = default_right,
    container: ContainerName = "dict",
) -> Union[dict, list, Node[T], NodeNT]:
    """Построить полное бинарное дерево рекурсивно.

    Args:
        height: Высота дерева (целое число >= 1). Узел без потомков — это высота 1.
        root: Значение в корне.
        left_fn: Функция вычисления значения левого потомка из значения родителя.
        right_fn: Функция вычисления значения правого потомка из значения родителя.
        container: Контейнер результата: "dict" | "list" | "dataclass" | "namedtuple".

    Returns:
        Структура дерева в выбранном контейнере.

    Raises:
        ValueError: Если height < 1 или указан неизвестный контейнер.
    """
    if height < 1:
        raise ValueError("height должен быть >= 1")

    # Базовый случай: лист
    if height == 1:
        if container == "dict":
            return {"value": root, "left": None, "right": None}
        if container == "list":
            return [root, None, None]
        if container == "dataclass":
            return Node(root, None, None)
        if container == "namedtuple":
            return NodeNT(root, None, None)
        raise ValueError(f"Неизвестный контейнер: {container!r}")

    # Вычисляем значения потомков и строим их рекурсивно
    left_value = left_fn(root)
    right_value = right_fn(root)

    left_sub = gen_bin_tree(
        height - 1,
        left_value,
        left_fn=left_fn,
        right_fn=right_fn,
        container=container,
    )
    right_sub = gen_bin_tree(
        height - 1,
        right_value,
        left_fn=left_fn,
        right_fn=right_fn,
        container=container,
    )

    # Упаковываем текущий узел согласно выбранному контейнеру
    if container == "dict":
        return {"value": root, "left": left_sub, "right": right_sub}
    if container == "list":
        return [root, left_sub, right_sub]
    if container == "dataclass":
        return Node(root, left_sub, right_sub)  # type: ignore[arg-type]
    if container == "namedtuple":
        return NodeNT(root, left_sub, right_sub)  # type: ignore[misc]

    raise ValueError(f"Неизвестный контейнер: {container!r}")


def _to_builtin(obj):
    """Вспомогательное: привести дерево к структурам dict/list для красивого вывода."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return {k: _to_builtin(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_builtin(v) for v in obj]
    if isinstance(obj, Node):
        return {"value": obj.value, "left": _to_builtin(obj.left), "right": _to_builtin(obj.right)}
    if isinstance(obj, NodeNT):
        return {"value": obj.value, "left": _to_builtin(obj.left), "right": _to_builtin(obj.right)}
    return obj


def main() -> None:
    """CLI-точка входа: сгенерировать дерево и напечатать его.

    Пример:
        python bin_tree.py --height 4 --root 8 --container dict
    """
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Рекурсивный генератор бинарного дерева.")
    parser.add_argument("--height", type=int, required=True, help="Высота дерева (>=1).")
    parser.add_argument("--root", type=float, required=True, help="Значение в корне.")
    parser.add_argument(
        "--container",
        type=str,
        default="dict",
        choices=["dict", "list", "dataclass", "namedtuple"],
        help="Тип контейнера результата.",
    )
    args = parser.parse_args()

    tree = gen_bin_tree(height=args.height, root=args.root, container=args.container)  # type: ignore[arg-type]
    print(json.dumps(_to_builtin(tree), ensure_ascii=False, indent=2))


__all__ = ["gen_bin_tree", "Node", "NodeNT", "default_left", "default_right"]

if __name__ == "__main__":
    main()

