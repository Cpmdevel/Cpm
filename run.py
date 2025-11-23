from __future__ import annotations

import os
import sys
from typing import List
from flask import Flask

from app import create_app, initialize_database
from app.seed import seed_demo_content


def _parse_port(argv: List[str]) -> int:
    # Priority: --port=XXXX, then --port XXXX, then env PORT, else 5000
    default_port = 5000
    for arg in argv:
        if arg.startswith("--port="):
            try:
                return int(arg.split("=", 1)[1])
            except ValueError:
                return default_port
    if "--port" in argv:
        try:
            idx = argv.index("--port")
            return int(argv[idx + 1])
        except (ValueError, IndexError):
            return default_port
    try:
        return int(os.environ.get("PORT", default_port))
    except ValueError:
        return default_port


def main(argv: List[str]) -> None:
    app: Flask = create_app()

    if "--init-db" in argv:
        initialize_database(app)
        print("Database initialized.")

    if "--seed-demo" in argv:
        with app.app_context():
            seed_demo_content()
        print("Demo content seeded.")

    if "--serve" in argv or not any(flag in argv for flag in ("--init-db", "--seed-demo")):
        # Default behavior: run the server
        initialize_database(app)
        port = _parse_port(argv)
        app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    main(sys.argv[1:])
