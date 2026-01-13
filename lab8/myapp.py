"""Application entry point."""

from __future__ import annotations

from myapp.controller import run_server


def main() -> None:
    """Start the server."""
    run_server()


if __name__ == "__main__":
    main()
