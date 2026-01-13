"""Lab 9 - MVC + SQLite (in-memory) + CRUD + routing.

Run:
    python app.py

Then open:
    http://localhost:8000/

Notes:
- The server uses GET routes for simplicity (as required in the task).
- SQLite works in-memory: data will be reset after restart.
"""

from __future__ import annotations

import http.server
import socketserver
from http import HTTPStatus
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse

from jinja2 import Environment, FileSystemLoader, select_autoescape

from controllers.currencycontroller import CurrencyController
from controllers.databasecontroller import (
    CurrencyRatesCRUD,
    Database,
    UserCRUD,
    UserCurrencyCRUD,
)
from controllers.pages import AuthorInfo, PagesController
from controllers.usercontroller import UserController


HOST = "127.0.0.1"
PORT = 8000


def _first(qs: dict[str, list[str]], key: str) -> Optional[str]:
    """Return first query-string value for *key* or None."""
    vals = qs.get(key)
    if not vals:
        return None
    return vals[0]


class AppRequestHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler with a very small custom router."""

    pages: PagesController
    currency: CurrencyController
    users: UserController

    def _send_html(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text: str, status: int = 200) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Location", location)
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802 (required name)
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        try:
            if path == "/":
                self._send_html(self.pages.index())
                return

            if path == "/author":
                self._send_html(self.pages.author_page())
                return

            if path == "/users":
                self._send_html(self.pages.users_page())
                return

            if path == "/user":
                user_id_raw = _first(qs, "id")
                if user_id_raw is None:
                    self._send_html(self.pages.message("Не передан параметр id"), status=400)
                    return
                self._send_html(self.pages.user_page(int(user_id_raw)))
                return

            if path == "/user/subscribe":
                user_id_raw = _first(qs, "id")
                currency_id_raw = _first(qs, "currency_id")
                if not user_id_raw or not currency_id_raw:
                    self._send_html(self.pages.message("Нужны параметры id и currency_id"), status=400)
                    return
                self.users.subscribe(int(user_id_raw), int(currency_id_raw))
                self._redirect(f"/user?id={user_id_raw}")
                return

            if path == "/user/unsubscribe":
                user_id_raw = _first(qs, "id")
                currency_id_raw = _first(qs, "currency_id")
                if not user_id_raw or not currency_id_raw:
                    self._send_html(self.pages.message("Нужны параметры id и currency_id"), status=400)
                    return
                self.users.unsubscribe(int(user_id_raw), int(currency_id_raw))
                self._redirect(f"/user?id={user_id_raw}")
                return

            if path == "/currencies":
                self._send_html(self.pages.currencies_page())
                return

            if path == "/currency/delete":
                currency_id_raw = _first(qs, "id")
                if currency_id_raw is None:
                    self._send_html(self.pages.message("Не передан параметр id"), status=400)
                    return
                self.currency.delete_currency(int(currency_id_raw))
                self._redirect("/currencies")
                return

            if path == "/currency/update":
                # Format: /currency/update?USD=91.2  (code is the key)
                updated = 0
                for key, values in qs.items():
                    if len(key) == 3 and key.isalpha() and values:
                        self.currency.update_currency(key, float(values[0]))
                        updated += 1
                self._redirect("/currencies" if updated else "/currencies")
                return

            if path == "/currency/create":
                num_code = _first(qs, "num_code")
                char_code = _first(qs, "char_code")
                name = _first(qs, "name")
                value = _first(qs, "value")
                nominal = _first(qs, "nominal")
                if None in (num_code, char_code, name, value, nominal):
                    self._send_html(self.pages.message("Не хватает параметров для создания валюты"), status=400)
                    return
                self.currency.create_currency(num_code, char_code, name, float(value), int(nominal))
                self._redirect("/currencies")
                return

            if path == "/currency/show":
                currencies = self.currency.list_currencies()
                print("\n".join(f"{c.id}: {c.char_code} = {c.value}" for c in currencies))
                self._send_text("OK (see server console)")
                return

            self._send_html(self.pages._render("error.html", message="404: Страница не найдена"), status=404)

        except Exception as exc:  # noqa: BLE001 (educational project)
            self._send_html(self.pages._render("error.html", message=str(exc)), status=500)

    def log_message(self, fmt: str, *args: Any) -> None:
        # Keep logs shorter for the lab.
        print(f"[{self.log_date_time_string()}] {self.address_string()} - {fmt % args}")


def build_app(author_full_name: str, group: str) -> type[AppRequestHandler]:
    """Create a configured request handler class."""
    db = Database(":memory:")
    currency_crud = CurrencyRatesCRUD(db.conn)
    users_crud = UserCRUD(db.conn)
    user_currency_crud = UserCurrencyCRUD(db.conn)

    currency_controller = CurrencyController(currency_crud)
    user_controller = UserController(users_crud, currency_crud, user_currency_crud)

    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    pages_controller = PagesController(
        env=env,
        author=AuthorInfo(full_name=author_full_name, group=group),
        currency_controller=currency_controller,
        user_controller=user_controller,
    )

    class _Handler(AppRequestHandler):
        pages = pages_controller
        currency = currency_controller
        users = user_controller

    return _Handler


def main() -> None:
    """Entry point."""
    handler = build_app(
        author_full_name="Затонских Никита Денисович",
        group="P-3123",
    )
    with socketserver.TCPServer((HOST, PORT), handler) as httpd:
        print(f"Server started: http://{HOST}:{PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
