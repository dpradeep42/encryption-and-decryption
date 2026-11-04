#!/usr/bin/env python3
"""Encrypt a file with Fernet.

With no arguments this encrypts the Medicare drug spending sample CSV and
writes EncryptedFile.csv, using myKey.key in the current directory. A key
file is created on first run when none is configured.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from cryptography.fernet import Fernet

from key_utils import add_key_argument, die, load_or_create_key, resolve_key_path

DEFAULT_INPUT = "health-medicare-drug-spending (1).csv"
DEFAULT_OUTPUT = "EncryptedFile.csv"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Encrypt a file with a Fernet key.")
    parser.add_argument(
        "-i",
        "--input",
        default=DEFAULT_INPUT,
        help=f"Plaintext file to encrypt (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Where to write the ciphertext (default: {DEFAULT_OUTPUT})",
    )
    add_key_argument(parser)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    source = Path(args.input)
    destination = Path(args.output)
    key_path = resolve_key_path(args.key)
    try:
        if source.resolve() == destination.resolve():
            raise ValueError("Input and output paths are the same.")
        if not source.is_file():
            raise FileNotFoundError(f"Input file not found: {source}")
        key, created = load_or_create_key(key_path)
        token = Fernet(key).encrypt(source.read_bytes())
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(token)
    except (OSError, ValueError) as exc:
        die(str(exc))
    if created:
        print(f"Created key at {key_path}")
    print(f"Encrypted {source} -> {destination}")


if __name__ == "__main__":
    main()
