#!/usr/bin/env python3
"""Create an ignored local .env with stable Browser secrets; never overwrite."""

import os
from pathlib import Path
import secrets


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    target = root / ".env"
    content = (root / ".env.example").read_text()
    content += f"\nAUTH_SECRET={secrets.token_hex(32)}\nENCRYPTION_KEY={secrets.token_hex(32)}\n"
    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        print(".env already exists; preserved. See .env.example for required keys.")
        return
    with os.fdopen(fd, "w") as file:
        file.write(content)
    print("Created .env with private permissions and generated Browser secrets (values hidden).")


if __name__ == "__main__":
    main()
