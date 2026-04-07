# Internal Repository Conventions — Pre-commit Hook

These are our organization's mandatory repository standards. All pre-commit hooks must enforce these rules.

## File Size
- Maximum staged file size: **2MB** (2097152 bytes), not the typical 5MB

## Python Quality
- All staged Python files must pass `ruff check --select=E,F,W` (not just syntax checking)
- No `import *` (wildcard imports) allowed in any staged Python file
- Debug `print()` calls must still be caught (lines with bare `print(` not in comments)

## Commit Message Format
- Commit messages must match: `^(feat|fix|chore|docs|refactor): [A-Z].+`
- The type prefix is required, followed by colon-space, then a capitalized description
- Note: pre-commit hooks cannot validate commit messages (that's commit-msg hook), but the hook should validate all other rules

## Forbidden Files
- Hard block on: `.env`, `.credentials`, `*.pem`, `*.key` files
- These must NEVER be committed regardless of content

## Binary Files
- Staged binary files must be located under `assets/bin/` directory
- Each binary file must have a corresponding `.meta` file (same name + `.meta` extension)

## Trailing Whitespace
- No trailing whitespace on any line in any staged file
