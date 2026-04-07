# Internal Repository Conventions — Key Rules

Our top 3 mandatory pre-commit rules:

1. **Commit message format**: must match `^(feat|fix|chore|docs|refactor): [A-Z].+`
2. **No credential files**: `.env`, `.credentials`, `*.pem`, `*.key` — hard block, never commit
3. **Python linting**: all staged Python files must pass `ruff check`
