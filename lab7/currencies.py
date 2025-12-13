"""
Получение курсов валют (только бизнес-логика).

Функция `get_currencies`:
- запрашивает JSON по указанному URL,
- извлекает словарь "Valute",
- возвращает словарь вида код->курс для запрошенных валют.

Логирование внутри функции отсутствует: функция только выбрасывает исключения,
а логирует их декоратор.
"""

from __future__ import annotations

import json
from typing import Dict, List
from urllib.error import URLError
from urllib.request import urlopen


def get_currencies(
    currency_codes: List[str],
    url: str = "https://www.cbr-xml-daily.ru/daily_json.js",
    timeout: float = 10.0,
) -> Dict[str, float]:
    """
    Получить курсы валют для указанных кодов.
    Параметры
    currency_codes:
        Список кодов валют (например ["USD", "EUR"]).
    url:
        Адрес API, возвращающего JSON с ключом "Valute".
    timeout:
        Таймаут сетевого запроса в секундах.
    Возвращает

    dict[str, float]
        Словарь соответствий: код валюты -> числовое значение курса.

    Исключения
    ConnectionError
        Если API недоступен или запрос завершился ошибкой.
    ValueError
        Если JSON некорректен.
    KeyError
        Если нет ключа "Valute" или запрошенной валюты нет в данных.
    TypeError
        Если курс валюты имеет неправильный тип (не int/float).
    """
    try:
        with urlopen(url, timeout=timeout) as response:
            raw = response.read()
    except (URLError, OSError) as exc:
        raise ConnectionError("API недоступен") from exc

    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Некорректный JSON") from exc

    valute = data["Valute"]  # KeyError если ключа нет
    if not isinstance(valute, dict):
        raise TypeError('Значение по ключу "Valute" должно быть словарём')

    result: Dict[str, float] = {}
    for code in currency_codes:
        entry = valute[code]  # KeyError если валюты нет
        if not isinstance(entry, dict):
            raise TypeError(f'Запись валюты "{code}" должна быть словарём')

        value = entry.get("Value")
        if not isinstance(value, (int, float)):
            raise TypeError(
                f'Курс валюты "{code}" имеет неверный тип: {type(value).__name__}'
            )

        result[code] = float(value)

    return result
