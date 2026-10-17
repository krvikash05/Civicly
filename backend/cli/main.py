"""CLI invokes services; it accepts no executable Cypher or write action."""

import argparse
import json

from pydantic import ValidationError
from redis.exceptions import RedisError

from app.config import Settings
from app.services.health import check_health
from app.graph.migration import MigrationError
from app.services.schema import schema_operation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="civicly")
    parser.add_argument("command", choices=["health", "migrate", "schema-status"])
    parser.add_argument("--env-file", default=".env", help="Local settings file (default: .env)")
    parser.add_argument("--retry-failed", action="store_true", help="Migration only: recreate known FAILED constraints after data repair")
    args = parser.parse_args(argv)
    if args.retry_failed and args.command != "migrate":
        parser.error("--retry-failed is only valid for migrate")
    try:
        settings = Settings(_env_file=args.env_file)
    except ValidationError:
        print(json.dumps({"status": "unavailable", "error_code": "CONFIG_INVALID"}))
        return 2
    if args.command != "health":
        try:
            result = schema_operation(settings, apply=args.command == "migrate", retry_failed=args.retry_failed)
        except MigrationError as error:
            print(json.dumps({"ready": False, "error_code": "SCHEMA_MIGRATION_ERROR", "message": str(error)}))
            return 1
        except RedisError:
            print(json.dumps({"ready": False, "error_code": "SCHEMA_MIGRATION_ERROR"}))
            return 1
        print(json.dumps(result))
        return 0 if result["ready"] else 1
    result = check_health(settings)
    print(result.model_dump_json())
    return 0 if result.status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
