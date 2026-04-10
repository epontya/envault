# envault

> A CLI tool to securely store and sync environment variables across projects using encrypted local vaults.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envault
```

---

## Usage

**Initialize a new vault in your project:**
```bash
envault init
```

**Add an environment variable:**
```bash
envault set DATABASE_URL "postgres://user:pass@localhost/mydb"
```

**Retrieve a variable:**
```bash
envault get DATABASE_URL
```

**Load all vault variables into your shell session:**
```bash
eval $(envault load)
```

**Sync vault across projects:**
```bash
envault sync --target ../other-project
```

All secrets are encrypted at rest using AES-256 encryption. A master password is required to unlock the vault.

---

## Requirements

- Python 3.8+
- `cryptography` library (installed automatically)

---

## License

This project is licensed under the [MIT License](LICENSE).

---

*envault — keep your secrets secret.*