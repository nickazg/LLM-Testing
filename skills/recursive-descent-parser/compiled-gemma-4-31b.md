# Expression Parser (Recursive Descent)

## AST Node Structure

```python
class ASTNode:
    def __init__(self, type, value=None, op=None, left=None, right=None, operand=None):
        self.type = type      # 'number', 'binop', or 'unary'
        self.value = value    # for numbers
        self.op = op          # for operators
        self.left = left      # for binary ops
        self.right = right
        self.operand = operand  # for unary ops

def num_node(v): return ASTNode('number', value=v)
def binop_node(op, left, right): return ASTNode('binop', op=op, left=left, right=right)
def unary_node(op, operand): return ASTNode('unary', op=op, operand=operand)
```

## Tokenizer

```python
import re

def tokenize(s):
    return re.findall(r'\d+\.?\d*|[+\-*/()]', s.strip())
```

## Parser (use a class for clear state management)

```python
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self):
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def parse(self):
        node = self.expression()
        if self.peek() is not None:
            raise ValueError("Extra tokens")
        return node

    def expression(self):
        # handles + and -
        node = self.term()
        while self.peek() in ('+', '-'):
            op = self.consume()
            node = binop_node(op, node, self.term())
        return node

    def term(self):
        # handles * and /
        node = self.unary()
        while self.peek() in ('*', '/'):
            op = self.consume()
            node = binop_node(op, node, self.unary())
        return node

    def unary(self):
        # handles unary minus
        if self.peek() == '-':
            self.consume()
            return unary_node('-', self.unary())
        return self.primary()

    def primary(self):
        # handles numbers and parentheses
        t = self.peek()
        if t == '(':
            self.consume()
            node = self.expression()
            if self.peek() != ')':
                raise ValueError("Missing )")
            self.consume()
            return node
        if t and t[0].isdigit():
            self.consume()
            return num_node(float(t))
        raise ValueError(f"Unexpected: {t}")

def parse(expr):
    tokens = tokenize(expr)
    if not tokens:
        raise ValueError("Empty expression")
    return Parser(tokens).parse()
```

## Evaluator

```python
def evaluate(node):
    if node.type == 'number':
        return node.value
    if node.type == 'unary':
        return -evaluate(node.operand)
    # binary operator
    l, r = evaluate(node.left), evaluate(node.right)
    return {'+': l+r, '-': l-r, '*': l*r, '/': l/r}[node.op]
```

**Key insight**: `expression` → `term` → `unary` → `primary`. Each function handles one precedence level and calls the next for tighter binding.
