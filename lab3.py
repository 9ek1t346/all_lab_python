"""
Дерево строится рекурсивно. Значения потомков вычисляются из значения узла x по
правилам:
  * left(x)  = x + x/2   (по умолчанию)
  * right(x) = x ** 2    (по умолчанию; ВАЖНО: возведение в степень, не XOR)

Параметры можно переопределять функциями left_rule/right_rule.
Представление дерева — вложенные словари (по умолчанию) либо Node.

есть тесты unittest, включая персональную проверку:
root=8, height=4, left=x + x/2, right=x ** 2.
"""

from __future__ import annotations

import unittest
from collections import namedtuple
from typing import Callable, Optional, Union, TypedDict

class DictNode(TypedDict, total=False):
    """Словарное представление узла бинарного дерева.

    Ключи:
        value: числовое значение узла.
        left: левое поддерево или None для листа.
        right: правое поддерево или None для листа.
    """
    value: float
    left: Optional['DictNode']
    right: Optional['DictNode']


NodeNT = namedtuple('Node', ('value', 'left', 'right'))

Rule = Callable[[float], float]
Tree = Union[DictNode, NodeNT]

#Генератор дерева

def gen_bin_tree(
    height: int,
    root: float,
    left_rule: Optional[Rule] = None,
    right_rule: Optional[Rule] = None,
    as_namedtuple: bool = False,
) -> Tree:
    """Сгенерировать полное бинарное дерево высоты *height* с корнем *root*.

    Функция рекурсивная. Для каждого узла со значением x создаются два потомка:
        left(x)  = left_rule(x)
        right(x) = right_rule(x)
    Аргументы:
        height: Количество уровней в дереве (>=1). При height=1 возвращается лист.
        root: Значение в корневом узле.
        left_rule: Функция вычисления левого потомка из x.
        right_rule: Функция вычисления правого потомка из x.
        as_namedtuple: Если True — возвращать дерево как Node(namedtuple),
            иначе — как вложенные словари.
    Возвращает:
        Дерево в выбранном представлении.
    """
    if height < 1:
        raise ValueError("height must be >= 1")

    # Правила по умолчанию — из задания/личной проверки.
    if left_rule is None:
        left_rule = lambda x: x + x / 2
    if right_rule is None:
        right_rule = lambda x: x ** 2

    def _make_node(value: float, left: Optional[Tree], right: Optional[Tree]) -> Tree:
        if as_namedtuple:
            return NodeNT(value, left, right)  # type: ignore[return-value]
        node: DictNode = {'value': float(value), 'left': left, 'right': right}
        return node  # type: ignore[return-value]

    if height == 1:
        return _make_node(float(root), None, None)

    x = float(root)
    left_value = left_rule(x)
    right_value = right_rule(x)

    left_subtree = gen_bin_tree(height - 1, left_value, left_rule, right_rule, as_namedtuple)
    right_subtree = gen_bin_tree(height - 1, right_value, left_rule, right_rule, as_namedtuple)
    return _make_node(x, left_subtree, right_subtree)

#Утилиты(для обоих представлений)

def tree_height(tree: Tree) -> int:
    """Вернуть высоту дерева (число уровней)."""
    if tree is None:
        return 0

    if isinstance(tree, NodeNT):
        left = tree.left
        right = tree.right
    else:
        left = tree.get('left')
        right = tree.get('right')

    if left is None and right is None:
        return 1
    return 1 + max(tree_height(left), tree_height(right))


def get_left(tree: Tree) -> Optional[Tree]:
    """Получить левое поддерево из любого поддерживаемого представления."""
    if isinstance(tree, NodeNT):
        return tree.left
    return tree.get('left')


def get_right(tree: Tree) -> Optional[Tree]:
    """Получить правое поддерево из любого поддерживаемого представления."""
    if isinstance(tree, NodeNT):
        return tree.right
    return tree.get('right')


def get_value(tree: Tree) -> float:
    """Получить значение узла из любого поддерживаемого представления."""
    if isinstance(tree, NodeNT):
        return float(tree.value)
    return float(tree['value'])

#Тесты

class TestGenBinTreeDefaults(unittest.TestCase):
    def test_personal_check_root8_h4(self):
        # Personal check: root=8, height=4, left=x + x/2, right=x ** 2
        t = gen_bin_tree(height=4, root=8)
        self.assertEqual(tree_height(t), 4)

        # Root
        self.assertAlmostEqual(get_value(t), 8.0)

        # Level 1 children
        l1_left = get_left(t)
        l1_right = get_right(t)
        self.assertIsNotNone(l1_left)
        self.assertIsNotNone(l1_right)
        self.assertAlmostEqual(get_value(l1_left), 12.0)  # 8 + 4
        self.assertAlmostEqual(get_value(l1_right), 64.0)  # 8 ** 2

        # Deeper samples:
        # Left->Left->Left: 8 -> 12 -> 18 -> 27
        l2_left = get_left(l1_left)
        l3_left = get_left(l2_left)
        self.assertAlmostEqual(get_value(l2_left), 18.0)
        self.assertAlmostEqual(get_value(l3_left), 27.0)

        # Right->Right->Left: 8 -> 64 -> 4096 -> 6144
        r2_right = get_right(l1_right)
        r3_left = get_left(r2_right)
        self.assertAlmostEqual(get_value(r2_right), 4096.0)
        self.assertAlmostEqual(get_value(r3_left), 6144.0)

    def test_height_one_leaf(self):
        t = gen_bin_tree(height=1, root=5)
        self.assertEqual(tree_height(t), 1)
        self.assertIsNone(get_left(t))
        self.assertIsNone(get_right(t))
        self.assertAlmostEqual(get_value(t), 5.0)

class TestGenBinTreeNamedtuple(unittest.TestCase):
    def test_namedtuple_representation(self):
        t = gen_bin_tree(height=3, root=2, as_namedtuple=True)
        self.assertIsInstance(t, NodeNT)
        self.assertEqual(tree_height(t), 3)
        self.assertAlmostEqual(get_value(t), 2.0)
        self.assertAlmostEqual(get_value(get_left(t)), 3.0)  # 2 + 1
        self.assertAlmostEqual(get_value(get_right(t)), 4.0)  # 2 ** 2

class TestCustomRules(unittest.TestCase):
    def test_custom_rules_simple(self):
        # Custom rules: left=x+1, right=x+2
        t = gen_bin_tree(height=3, root=1,
                         left_rule=lambda x: x + 1,
                         right_rule=lambda x: x + 2)
        self.assertAlmostEqual(get_value(get_left(t)), 2.0)
        self.assertAlmostEqual(get_value(get_right(t)), 3.0)
        self.assertAlmostEqual(get_value(get_left(get_left(t))), 3.0)
        self.assertAlmostEqual(get_value(get_right(get_left(t))), 4.0)

    # Keep only the runner inside the guard.
    if __name__ == "__main__":
        unittest.main()