# Pre-commit Hook Rules

## Required Checks

### 1. File Size
- Max: 2MB (2097152 bytes) per file

### 2. Forbidden Files (block completely)
- `.env`, `.credentials`, `*.pem`, `*.key`

### 3. Python Files (.py)
- Run: `ruff check --select=E,F,W <file>`
- Block wildcard imports: lines matching `from .+ import \*`
- Block debug prints: lines with `print(` (not in comments)

### 4. Binary Files
- Must be in `assets/bin/` directory
- Must have matching `.meta` file (e.g., `foo.bin` needs `foo.bin.meta`)

### 5. All Files
- No trailing whitespace on any line

## Implementation Notes

- Use `subprocess.run()` for ruff checks
- Return non-zero exit code on any violation
- Print clear error messages for failures
