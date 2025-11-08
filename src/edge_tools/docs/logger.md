# Logging Framework

This project uses Python’s built-in `logging` module.  
Logging replaces `print()` so we can control verbosity (INFO vs DEBUG), organize messages by module, and enable or disable detailed output without changing code.

---

## 1. Setup Function (Configure Once)

Create a file named `logger.py` (do **not** call it `logging.py`):

```python
# src/package/logger.py

import logging
import sys

def setup_logging(level=logging.INFO):
    """Configure global logging settings."""
    logger = logging.getLogger()
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(handler)
```

---

## 2. Main Entry Point

Initialize logging **once** when the program starts.

```python
# main.py

from src.package.logger import setup_logging
import logging

def main():
    setup_logging(logging.INFO)  # choose INFO, DEBUG, WARNING, etc.

    # Application logic starts here
    pass

if __name__ == "__main__":
    main()
```

---

## 3. Use Logging in Any Module

Every file gets its own logger:

```python
# src/package/database.py

import logging
logger = logging.getLogger(__name__)

def run_query(q):
    logger.info("Running query...")
    logger.debug("SQL: %s", q)
```

Never use `print()` — always use `logger`.

---

## 4. Switching Verbosity

Show normal output:

```python
setup_logging(logging.INFO)
```

Show everything (debug mode):

```python
setup_logging(logging.DEBUG)
```

---

## 5. Optional: Switch Level at Runtime

Run program normally:

```
uv run python main.py
```

Run in debug mode:

```
LOG_LEVEL=DEBUG uv run python main.py
```

Modify `main.py` to support that:

```python
import os
level = os.getenv("LOG_LEVEL", "INFO").upper()
setup_logging(getattr(logging, level))
```

---

## 6. Log Level Cheat Sheet

| Level      | Meaning                              | Example Use               |
| ---------- | ------------------------------------ | ------------------------- |
| `DEBUG`    | Show everything                      | development, tracing code |
| `INFO`     | Normal execution logs                | progress messages         |
| `WARNING`  | Something unexpected but recoverable | retrying, skipping        |
| `ERROR`    | Operation failed, program continues  | network/API/IO errors     |
| `CRITICAL` | Program cannot continue              | fatal crash, shutdown     |

---

## Summary

* Logging is configured **once** in `main.py`
* Other modules call `logging.getLogger(__name__)`
* Debug output stays in the code forever, just toggle the level
* This keeps code clean, traceable, and production-safe

```

---

If you want, I’ll now give you a **colored log formatter** so WARNINGS and ERRORS stand out visually in the terminal.  
Just say:

> give color logs 🌈
```
