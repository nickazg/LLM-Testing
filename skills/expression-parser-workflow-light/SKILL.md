# Expression Parser — Approach & Guardrails

## Approach
Build a recursive descent parser with operator precedence. Separate the work into three clean stages: tokenize, parse into AST, then evaluate the AST.

## Key Guardrails

- **Tokenize first** — don't try to parse raw characters directly. Build a token list, then consume tokens during parsing. This avoids most ambiguity bugs.
- **Precedence via grammar rules** — implement as separate functions: expression handles +/-, term handles *// , unary handles negation, primary handles numbers and parentheses. Each level calls the next.
- **Unary minus ambiguity** — `-3+5` and `-(3+2)` must both work. Unary minus binds tighter than binary operators. Handle it at the unary level, not as a special case in binary parsing.
- **Parentheses** — consume the opening `(`, recursively parse the inner expression, then expect and consume `)`. Raise ValueError if `)` is missing.
- **Empty input** — raise ValueError, don't return 0 or None.
- **Division by zero** — raise ZeroDivisionError during evaluation, not during parsing.
- **Return floats** — even `4/2` should return `2.0`, not `2`. Use float throughout evaluation.
- **Unexpected tokens** — if tokens remain after parsing a complete expression, that's an error.
