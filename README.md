# File encryption and decryption

Encrypt and decrypt files with Fernet symmetric encryption from the
`cryptography` library.

## What it does

- `keyCreation.py` writes a new Fernet key file.
- `encryption.py` reads a file and writes the ciphertext.
- `decryption.py` reads that ciphertext with the same key and writes the original bytes back.

With no arguments, `encryption.py` encrypts `health-medicare-drug-spending (1).csv`
and writes `EncryptedFile.csv`. `decryption.py` reads `EncryptedFile.csv` and
writes `DecryptedFile.csv`. The whole file is loaded into memory and stored as
one Fernet token, which is the same operation these scripts performed before.

## Setup

Python 3.9 or newer is required, except 3.9.0 and 3.9.1. Tested with
Python 3.12.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the environment with `venv\Scripts\activate`.

Run the commands below from the repository root.

## Usage

Create a key, or let `encryption.py` create `myKey.key` the first time it runs
and no key file is present:

```bash
python keyCreation.py
python keyCreation.py --key "$HOME/.keys/medicare.key"
```

`keyCreation.py` does not replace an existing key file unless you pass
`--force`. Replacing a key means files encrypted with the old key will not
decrypt.

Choose the key file with `--key` or the `KEY_PATH` environment variable.
`--key` takes priority. If neither is set, the scripts use `myKey.key` in the
current directory.

```bash
export KEY_PATH="$HOME/.keys/medicare.key"
python encryption.py
python decryption.py
```

Paths can also be set explicitly:

```bash
python encryption.py \
  --input "health-medicare-drug-spending (1).csv" \
  --output EncryptedFile.csv \
  --key "$HOME/.keys/medicare.key"

python decryption.py \
  --input EncryptedFile.csv \
  --output DecryptedFile.csv \
  --key "$HOME/.keys/medicare.key"
```

`decryption.py` does not create a key. It needs the key that encrypted the
file. After a round trip, `DecryptedFile.csv` matches the input byte for byte.

## Sample data

`health-medicare-drug-spending (1).csv` is the plaintext sample (Medicare drug
spending rows).

`EncryptedFile.csv` used to be committed. It could only be decrypted with the
key in `myKey.key`, and that key was committed beside it. Those files are no
longer tracked. Encrypt the sample when you want ciphertext; the output is
written at runtime and is listed in `.gitignore`.

`DecryptedFile.csv` was a byte-for-byte copy of the sample CSV, produced by
decrypting that committed ciphertext. It is not tracked either. `decryption.py`
writes it at runtime.

## Security

Do not commit encryption keys. Keys must stay out of git. `.gitignore` ignores
`*.key`, `.env`, virtual environments, `__pycache__/`, `.idea/`, and the
runtime files `EncryptedFile.csv` and `DecryptedFile.csv`.

`myKey.key` was committed in an earlier revision and is still reachable from
git history. This repository does not rewrite that history. Treat the old key
as public, do not reuse it, and re-encrypt anything that was protected with it.

New key files are written with mode `0600` (owner read and write). If an
existing key file is readable by the group or by others, the scripts print a
warning. Keep the key separate from ciphertext you share. Anyone who has the
key can decrypt every file encrypted with it.

Fernet checks integrity before it returns plaintext. Decryption fails when the
key is wrong or the ciphertext has been modified.

## License

MIT. Copyright (c) 2026 Pradeep Kumar Dasari. See [LICENSE](LICENSE).
