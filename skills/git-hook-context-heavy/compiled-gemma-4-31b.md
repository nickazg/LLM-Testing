# Pre-commit Hook Implementation

## Checks (fail on any violation)

### 1. File Size
- Max 2097152 bytes (2MB) per staged file

### 2. Forbidden Files
- Block: `.env`, `.credentials`, `*.pem`, `*.key`

### 3. Python Files (.py)
- Run `ruff check --select=E,F,W <file>` via subprocess
- Reject `from ... import *` patterns
- Reject lines containing `print(` (except in comments)

### 4. Binary Files
- Must be under `assets/bin/`
- Must have matching `.meta` file (e.g., `data.bin` → `data.bin.meta`)

### 5. Trailing Whitespace
- No trailing whitespace in any staged file

## Output

- Exit 0 if all checks pass
- Exit 1 and print violations if any fail
