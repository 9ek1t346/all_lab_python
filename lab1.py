from typing import Optional, List
import unittest


def to_sum(nums: List[int], turget: int) -> Optional[List[int]]:
    res = {}  # для числа и его индекса
    for i, x in enumerate(nums):  # идем по массиву и сохраняем в res индексы чисел
        need = turget - x  # проверяю для каждого нового числа x был ли его партнер раньше: target - x
        if need in res:  # запись после проверки гарантирует не использовать элемент дважды
            return [res[need], i]  # если да — возвращаю сразу пару индексов чисел
        res[x] = i  # если нет — заношу x в res и иду дальше
    return None


class TestToSum(unittest.TestCase):
    def assert_valid_pair(self, nums, target, pair):
        self.assertIsNotNone(pair, "Ожидалась пара индексов, но получено None")
        i, j = pair
        self.assertIsInstance(i, int)
        self.assertIsInstance(j, int)
        self.assertNotEqual(i, j, "Нельзя использовать один и тот же элемент дважды")
        self.assertGreaterEqual(i, 0)
        self.assertGreaterEqual(j, 0)
        self.assertLess(i, len(nums))
        self.assertLess(j, len(nums))
        self.assertEqual(nums[i] + nums[j], target, "Сумма по возвращённым индексам не равна цели")

    #Пограничные случаи
    def test_empty_list_returns_none(self):
        self.assertIsNone(to_sum([], 0))

    def test_single_element_returns_none(self):
        self.assertIsNone(to_sum([5], 5))

    def test_no_pair_when_only_one_occurrence_of_needed_value(self):
        # target = 6, единственная "кандидатная" тройка — 3, но второй 3 нет
        self.assertIsNone(to_sum([3, 2, 5], 6))

    def test_two_elements_match(self):
        self.assertEqual(to_sum([1, 2], 3), [0, 1])

    def test_two_elements_no_match(self):
        self.assertIsNone(to_sum([1, 2], 5))

    #Дубликаты, нули, отрицательные значения
    def test_duplicates_same_number(self):
        #Нужно взять два одинаковых числа
        pair = to_sum([2, 2], 4)
        self.assert_valid_pair([2, 2], 4, pair)
        self.assertEqual(pair, [0, 1])

    def test_zeros_pair(self):
        nums = [0, 4, 3, 0]
        pair = to_sum(nums, 0)
        self.assert_valid_pair(nums, 0, pair)
        self.assertEqual(pair, [0, 3])

    def test_negative_and_positive(self):
        nums = [-3, 4, 3, 90]
        pair = to_sum(nums, 0)
        self.assert_valid_pair(nums, 0, pair)
        self.assertEqual(pair, [0, 2])

    #Несколько возможных пар: возвращаемая - первая по порядку обхода
    def test_multiple_pairs_returns_first_by_order(self):
        nums = [1, 3, 2, 4]  # пары к 5: (1,4) и (3,2); первая найденная - индексы (1,2)
        self.assertEqual(to_sum(nums, 5), [1, 2])

    #Большие значения и длинные массивы
    def test_large_values(self):
        nums = [10**9, 3, 10**9 - 3]
        pair = to_sum(nums, 10**9)
        self.assert_valid_pair(nums, 10**9, pair)
        # конкретная ожидаемая пара
        self.assertEqual(pair, [1, 2])

    def test_long_list_tail_pair(self):
        #Пара находится в самом конце - проверяем, что алгоритм корректно её находит
        nums = list(range(10000))
        target = 19997
        self.assertEqual(to_sum(nums, target), [9998, 9999])

if __name__ == "__main__":
    unittest.main()