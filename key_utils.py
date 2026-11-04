"""Locate, create, and load the Fernet key used by the scripts.

The key path comes from --key, then the KEY_PATH environment variable, then
myKey.key in the current directory. Key material is never printed.
"""

from __future__ import annotations

import argparse
import binascii
import os
import shlex
import sys
from pathlib import Path

from cryptography.fernet import Fernet

DEFAULT_KEY_FILENAME = "myKey.key"
KEY_PATH_ENV = "KEY_PATH"


def add_key_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-k",
        "--key",
        default=None,
        help=(
            f"Path to the Fernet key file. Overrides the {KEY_PATH_ENV} "
            f"environment variable. Default: {DEFAULT_KEY_FILENAME} in the "
            "current directory."
        ),
    )


def resolve_key_path(cli_path: str | None) -> Path:
    """Return the key path from --key, KEY_PATH, or the default filename."""
    if cli_path:
        return Path(cli_path).expanduser()
    env_path = os.environ.get(KEY_PATH_ENV, "").strip()
    if env_path:
        return Path(env_path).expanduser()
    return Path(DEFAULT_KEY_FILENAME)


def die(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def _write_private(path: Path, data: bytes, exclusive: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT
    flags |= os.O_EXCL if exclusive else os.O_TRUNC
    fd = os.open(path, flags, 0o600)
    try:
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            if written == 0:
                raise OSError(f"Failed to write key file {path}")
            view = view[written:]
        os.fsync(fd)
    except Exception:
        os.close(fd)
        if exclusive:
            path.unlink(missing_ok=True)
        raise
    else:
        os.close(fd)
    os.chmod(path, 0o600)


def validate_key(key: bytes) -> bytes:
    key = key.strip()
    if not key:
        raise ValueError("Key file is empty.")
    try:
        Fernet(key)
    except (ValueError, TypeError, binascii.Error) as exc:
        raise ValueError("Key file is not a valid Fernet key.") from exc
    return key


def warn_if_key_is_shared(path: Path) -> None:
    try:
        mode = path.stat().st_mode
    except OSError:
        return
    if mode & 0o077:
        print(
            f"Warning: {path} is accessible to group or others. "
            f"Restrict it with: chmod 600 {shlex.quote(str(path))}",
            file=sys.stderr,
        )


def load_key(path: Path) -> bytes:
    if not path.is_file():
        raise FileNotFoundError(
            f"No key file at {path}. Run keyCreation.py, or pass --key / "
            f"set {KEY_PATH_ENV} to an existing key."
        )
    warn_if_key_is_shared(path)
    return validate_key(path.read_bytes())


def create_key(path: Path, force: bool = False) -> bytes:
    """Write a new Fernet key. Refuses to replace an existing file unless force."""
    if path.exists() and not force:
        raise FileExistsError(
            f"Key file already exists at {path}. Refusing to overwrite it. "
            "Pass --force to replace it. Ciphertext written with the old key "
            "will not decrypt with the new one."
        )
    if path.is_dir():
        raise IsADirectoryError(f"{path} is a directory.")
    key = Fernet.generate_key()
    _write_private(path, key, exclusive=not force)
    return key


def load_or_create_key(path: Path) -> tuple[bytes, bool]:
    """Return (key, created). Create the file only when it is missing."""
    if path.is_file():
        return load_key(path), False
    if path.exists():
        raise FileExistsError(f"{path} exists and is not a regular file.")
    try:
        key = create_key(path, force=False)
    except FileExistsError:
        return load_key(path), False
    return key, True
