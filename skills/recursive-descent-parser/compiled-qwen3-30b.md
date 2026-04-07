# Recursive Descent Expression Parser

## AST Node Structure

```python
class ASTNode:
    def __init__(self, type, value=None, op=None, left=None, right=None, operand=None):
        self.type = type        # 'number', 'binop', or 'unary'
        self.value = value      # float (for 'number')
        self.op = op            # str: '+', '-', '*', '/' (for 'binop') or '-' (for 'unary')
        self.left = left        # ASTNode (left operand for 'binop')
        self.right = right      # ASTNode (right operand for 'binop')
        self.operand = operand  # ASTNode (child for 'unary')
```

## Parser Class

Tokenize input, then parse following operator precedence (lowest to highest):
- **expression**: handles `+` and `-`
- **term**: handles `*` and `/`
- **unary**: handles unary minus `-`
- **primary**: handles numbers and parentheses

```python
import re

class Parser:
    def __init__(self, expression):
        # Tokenize: numbers (int/float) and operators/parentheses
        self.tokens = re.findall(r'\d+\.?\d*|[+\-*/()]', expression.strip())
        if not self.tokens:
            raise ValueError("Empty expression")
        self.pos = 0

    def parse(self):
        result = self.parse_expression()
        if self.pos < len(self.tokens):
            raise ValueError("Unexpected tokens after expression")
        return result

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self):
        token = self.peek()
        self.pos += 1
        return token

    # Lowest precedence: addition/subtraction
    def parse_expression(self):
        node = self.parse_term()
        while self.peek() in ('+', '-'):
            op = self.consume()
            right = self.parse_term()
            node = ASTNode('binop', op=op, left=node, right=right)
        return node

    # Higher precedence: multiplication/division
    def parse_term(self):
        node = self.parse_unary()
        while self.peek() in ('*', '/'):
            op = self.consume()
            right = self.parse_unary()
            node = ASTNode('binop', op=op, left=node, right=right)
        return node

    # Unary minus (right-associative)
    def parse_unary(self):
        if self.peek() == '-':
            self.consume()
            operand = self.parse_unary()
            return ASTNode('unary', op='-', operand=operand)
        return self.parse_primary()

    # Highest precedence: numbers and parentheses
    def parse_primary(self):
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        if token == '(':
            self.consume()
            node = self.parse_expression()
            if self.peek() != ')':
                raise ValueError("Unmatched parenthesis")
            self.consume()
            return node
        if re.match(r'\d', token):
            self.consume()
            return ASTNode('number', value=float(token))
        raise ValueError(f"Unexpected token: {token}")
```

## Evaluator

Recursively evaluate the AST:
```python
def evaluate(node):
    if node.type == 'number':
        return node.value
    if node.type == 'unary':
        return -evaluate(node.operand)
    if node.type == 'binop':
        left = evaluate(node.left)
        right = evaluate(node.right)
        if node.op == '+': return left + right
        if node.op == '-': return left - right
        if node.op == '*': return left * right
        if node.op == '/': return left / right
    raise ValueError(f"Unknown node type: {node.type}")
```

## Usage

```python
parser = Parser("3 + 4 * 2")
ast = parser.parse()
result = evaluate(ast)  # 11.0
```
