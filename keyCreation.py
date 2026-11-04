#!/usr/bin/env python3
"""Create a Fernet key file.

The key is written to --key, KEY_PATH, or myKey.key. An existing key file
is left in place unless --force is passed.
"""

from __future__ import annotations

import argparse

from key_utils import add_key_argument, create_key, die, resolve_key_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a Fernet key file.")
    add_key_argument(parser)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing key file. Ciphertext from the old key will not decrypt.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    key_path = resolve_key_path(args.key)
    try:
        create_key(key_path, force=args.force)
    except (OSError, ValueError) as exc:
        die(str(exc))
    print(f"Wrote key to {key_path}")


if __name__ == "__main__":
    main()
