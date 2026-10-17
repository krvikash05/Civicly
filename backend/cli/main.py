"""CLI invokes services; it accepts no executable Cypher or write action."""

import argparse
import json

from pydantic import ValidationError

from app.config import Settings
from app.services.health import check_health


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="civicly")
    parser.add_argument("command", choices=["health"])
    parser.add_argument("--env-file", default=".env", help="Local settings file (default: .env)")
    args = parser.parse_args(argv)
    try:
        settings = Settings(_env_file=args.env_file)
    except ValidationError:
        print(json.dumps({"status": "unavailable", "error_code": "CONFIG_INVALID"}))
        return 2
    result = check_health(settings)
    print(result.model_dump_json())
    return 0 if result.status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
