"""
Модульные тесты для get_currencies и декоратора logger.

Запуск:
    python -m unittest -v
"""

from __future__ import annotations

import io
import json
import unittest
from unittest.mock import patch
from urllib.error import URLError

from currencies import get_currencies
from logger import logger


class MockHTTPResponse:
    """Минимальная заглушка ответа urllib: context manager + read()."""

    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self) -> bytes:
        """Вернуть полезную нагрузку в байтах."""
        return self._payload

    def __enter__(self) -> "MockHTTPResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class TestGetCurrencies(unittest.TestCase):
    """Тесты бизнес-логики получения курсов (без логирования внутри)."""

    @patch("currencies.urlopen")
    def test_success_returns_rates(self, mock_urlopen) -> None:
        payload = {"Valute": {"USD": {"Value": 93.25}, "EUR": {"Value": 101.7}}}
        mock_urlopen.return_value = MockHTTPResponse(json.dumps(payload).encode("utf-8"))

        result = get_currencies(["USD", "EUR"], url="http://test")
        self.assertEqual(result, {"USD": 93.25, "EUR": 101.7})

    @patch("currencies.urlopen")
    def test_missing_currency_raises_keyerror(self, mock_urlopen) -> None:
        payload = {"Valute": {"USD": {"Value": 93.25}}}
        mock_urlopen.return_value = MockHTTPResponse(json.dumps(payload).encode("utf-8"))

        with self.assertRaises(KeyError):
            get_currencies(["EUR"], url="http://test")

    @patch("currencies.urlopen")
    def test_invalid_json_raises_valueerror(self, mock_urlopen) -> None:
        mock_urlopen.return_value = MockHTTPResponse(b"not-json")

        with self.assertRaises(ValueError):
            get_currencies(["USD"], url="http://test")

    @patch("currencies.urlopen")
    def test_connection_error_raises_connectionerror(self, mock_urlopen) -> None:
        mock_urlopen.side_effect = URLError("boom")

        with self.assertRaises(ConnectionError):
            get_currencies(["USD"], url="http://test")

    @patch("currencies.urlopen")
    def test_missing_valute_key_raises_keyerror(self, mock_urlopen) -> None:
        payload = {"NoValute": {}}
        mock_urlopen.return_value = MockHTTPResponse(json.dumps(payload).encode("utf-8"))

        with self.assertRaises(KeyError):
            get_currencies(["USD"], url="http://test")


class TestLoggerDecorator(unittest.TestCase):
    """Тесты поведения логирования декоратора через io.StringIO."""

    def setUp(self) -> None:
        self.stream = io.StringIO()

        @logger(handle=self.stream)
        def test_function(x: int) -> int:
            return x * 2

        @logger(handle=self.stream)
        def failing() -> None:
            raise ConnectionError("API down")

        self.test_function = test_function
        self.failing = failing

    def test_logs_success(self) -> None:
        result = self.test_function(3)
        self.assertEqual(result, 6)

        logs = self.stream.getvalue()
        self.assertIn("Старт test_function", logs)
        self.assertIn("test_function успешно завершилась", logs)
        self.assertIn("result=6", logs)

    def test_logs_error_and_reraises(self) -> None:
        with self.assertRaises(ConnectionError):
            self.failing()

        logs = self.stream.getvalue()
        self.assertIn("ERROR", logs)
        self.assertIn("ConnectionError", logs)
        self.assertIn("API down", logs)

    def test_context_example_like_assignment(self) -> None:
        stream = io.StringIO()

        @logger(handle=stream)
        def wrapped() -> dict:
            return get_currencies(["USD"], url="https://invalid")

        with self.assertRaises(ConnectionError):
            wrapped()

        logs = stream.getvalue()
        self.assertIn("ERROR", logs)
        self.assertIn("ConnectionError", logs)


if __name__ == "__main__":
    unittest.main()
