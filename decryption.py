#!/usr/bin/env python3
"""Decrypt a file with Fernet.

With no arguments this reads EncryptedFile.csv and writes DecryptedFile.csv,
using the same key encryption.py used. This script does not create a key.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from key_utils import add_key_argument, die, load_key, resolve_key_path

DEFAULT_INPUT = "EncryptedFile.csv"
DEFAULT_OUTPUT = "DecryptedFile.csv"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decrypt a file with a Fernet key.")
    parser.add_argument(
        "-i",
        "--input",
        default=DEFAULT_INPUT,
        help=f"Ciphertext file to decrypt (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Where to write the plaintext (default: {DEFAULT_OUTPUT})",
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
        key = load_key(key_path)
        plaintext = Fernet(key).decrypt(source.read_bytes())
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(plaintext)
    except InvalidToken:
        die(
            "Decryption failed. The key does not match this file, "
            "or the ciphertext was modified."
        )
    except (OSError, ValueError) as exc:
        die(str(exc))
    print(f"Decrypted {source} -> {destination}")


if __name__ == "__main__":
    main()
