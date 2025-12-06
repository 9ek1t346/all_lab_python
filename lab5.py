"""

Этот модуль предоставляет функцию `gen_bin_tree`, которая строит *полное* бинарное
дерево заданной высоты, начиная с числового корня, используя пользовательские
функции для вычисления значений левого и правого потомков. Реализация
**нерекурсивная** и поддерживает три формата результата:
- вложенные dict'ы;
- список значений в порядке уровней (heap-представление);
- список смежности (OrderedDict) с NodeNT(value, left, right).

Параметры по умолчанию соответствуют варианту из задания:
- root = 8
- height = 4
- левый потомок: r + r/2
- правый потомок: r ** 2
"""

from __future__ import annotations

from typing import Any, Callable, Deque, Dict, Literal, Mapping, Optional, Tuple, Union
from collections import deque, OrderedDict, namedtuple
import unittest

# Реализация

NodeNT = namedtuple("NodeNT", ["value", "left", "right"])


def _validate_height(height: int) -> None:
    """Проверяет, что высота — положительное целое число."""
    if not isinstance(height, int):
        raise TypeError("height must be an int")
    if height < 1:
        raise ValueError("height must be >= 1")


def gen_bin_tree(
    height: int = 4,
    root: Union[int, float] = 8,
    left_branch: Callable[[Union[int, float]], Union[int, float]] = lambda r: r + r / 2,
    right_branch: Callable[[Union[int, float]], Union[int, float]] = lambda r: r ** 2,
    container: Literal["dict", "list", "adjlist"] = "dict",
) -> Union[Dict[str, Any], list, "OrderedDict[int, NodeNT]"]:
    """Нерекурсивно генерирует полное бинарное дерево.

    Поддерживаемые форматы результата (аргумент *container*):
    - "dict" (по умолчанию): вложенные словари с ключами "value" | "left" | "right".
      Пример: {'value': 8, 'left': {...}, 'right': {...}}.
    - "list": массив значений в порядке уровней (heap). Для высоты h длина = 2**h - 1.
      Дети узла i находятся по индексам 2*i + 1 и 2*i + 2.
    - "adjlist": OrderedDict (индекс уровня -> NodeNT(value, left, right)), где
      left/right — индексы детей или None для листьев.

    Параметры
    height:
        Количество уровней (корень — уровень 1). Должно быть >= 1.
    root:
        Значение в корне (число).
    left_branch:
        Функция вычисления значения левого потомка по значению родителя.
        По умолчанию: lambda r: r + r/2.
    right_branch:
        Функция вычисления значения правого потомка по значению родителя.
        По умолчанию: lambda r: r ** 2 (квадрат).
    container:
        "dict" | "list" | "adjlist" — выбирает формат результата.

    Возвращает

    dict | list | OrderedDict[int, NodeNT]
        Дерево в выбранном представлении.

    Замечания

    - Реализация без рекурсии: для "dict" и "adjlist" — очередь (BFS),
      для "list" — индексация по формулам.
    - Дерево строится полным: у каждого внутреннего узла ровно два ребёнка.
    """
    _validate_height(height)

    if container not in {"dict", "list", "adjlist"}:
        raise ValueError('container must be one of {"dict", "list", "adjlist"}')

#Список
    if container == "list":
        size = (1 << height) - 1  # 2**height - 1
        arr = [None] * size
        arr[0] = root
        # Последний внутренний индекс (у которого ещё есть дети):
        last_internal = (1 << (height - 1)) - 2
        for i in range(0, last_internal + 1):
            parent_val = arr[i]
            li, ri = 2 * i + 1, 2 * i + 2
            arr[li] = left_branch(parent_val)
            arr[ri] = right_branch(parent_val)
        return arr

#Вложенные dict'ы
    if container == "dict":
        root_node: Dict[str, Any] = {"value": root, "left": None, "right": None}
        q: Deque[Tuple[Dict[str, Any], int]] = deque([(root_node, 1)])
        while q:
            node_map, level = q.popleft()
            if level >= height:
                continue  # лист
            parent_val = node_map["value"]
            left_node: Dict[str, Any] = {
                "value": left_branch(parent_val),
                "left": None,
                "right": None,
            }
            right_node: Dict[str, Any] = {
                "value": right_branch(parent_val),
                "left": None,
                "right": None,
            }
            node_map["left"] = left_node
            node_map["right"] = right_node
            q.append((left_node, level + 1))
            q.append((right_node, level + 1))
        return root_node

#Список смежности
    adj: "OrderedDict[int, NodeNT]" = OrderedDict()
    q2: Deque[Tuple[int, Union[int, float], int]] = deque([(0, root, 1)])
    while q2:
        idx, val, level = q2.popleft()
        if level >= height:
            adj[idx] = NodeNT(val, None, None)
            continue
        left_val = left_branch(val)
        right_val = right_branch(val)
        left_idx, right_idx = 2 * idx + 1, 2 * idx + 2
        adj[idx] = NodeNT(val, left_idx, right_idx)
        q2.append((left_idx, left_val, level + 1))
        q2.append((right_idx, right_val, level + 1))
    return adj


# Вспомогательные функции (для тестов/удобства)
def dict_tree_height(tree: Mapping[str, Any]) -> int:
    """Возвращает высоту дерева во вложенных dict'ах (рекурсивно, только для тестов)."""
    if not tree:
        return 0
    left_h = dict_tree_height(tree["left"]) if tree.get("left") else 0
    right_h = dict_tree_height(tree["right"]) if tree.get("right") else 0
    return 1 + max(left_h, right_h)


def dict_tree_as_list(tree: Mapping[str, Any]) -> list:
    """Преобразует дерево (вложенные dict'ы) в список значений по уровням (BFS)."""
    out = []
    q: Deque[Optional[Mapping[str, Any]]] = deque([tree])
    while q:
        node = q.popleft()
        if node is None:
            out.append(None)
            continue
        out.append(node["value"])
        q.append(node.get("left"))
        q.append(node.get("right"))
    while out and out[-1] is None:
        out.pop()
    return out

# Тесты
class TestGenBinTree(unittest.TestCase):
    def setUp(self):
        self.h = 4
        self.root = 8
        self.lb = lambda r: r + r / 2
        self.rb = lambda r: r ** 2

    def test_list_container_values_match_variant(self):
        arr = gen_bin_tree(self.h, self.root, self.lb, self.rb, container="list")
        expected_prefix = [8, 12, 64, 18, 144, 96, 4096]
        self.assertEqual(arr[:7], expected_prefix)
        self.assertEqual(len(arr), (1 << self.h) - 1)

    def test_dict_container_shape_and_values(self):
        tree = gen_bin_tree(self.h, self.root, self.lb, self.rb, container="dict")
        self.assertEqual(dict_tree_height(tree), self.h)
        level_order = dict_tree_as_list(tree)
        expected_prefix = [8, 12, 64, 18, 144, 96, 4096]
        self.assertEqual(level_order[:7], expected_prefix)

    def test_adjlist_container_basic(self):
        adj = gen_bin_tree(self.h, self.root, self.lb, self.rb, container="adjlist")
        self.assertEqual(adj[0].value, 8)
        self.assertEqual(adj[0].left, 1)
        self.assertEqual(adj[0].right, 2)
        self.assertEqual(len(adj), (1 << self.h) - 1)
        self.assertIsInstance(adj, OrderedDict)
        self.assertTrue(all(isinstance(v, NodeNT) for v in adj.values()))

    def test_custom_formulas_override_defaults(self):
        arr = gen_bin_tree(
            2, 8,
            left_branch=lambda r: r - 1,
            right_branch=lambda r: r + 1,
            container="list"
        )
        self.assertEqual(arr[:3], [8, 7, 9])

    def test_invalid_height(self):
        with self.assertRaises(ValueError):
            gen_bin_tree(0, 8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
