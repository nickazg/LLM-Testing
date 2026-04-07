# Expression Parser (Simplified)

## AST Node

```python
class ASTNode:
    def __init__(self, type, value=None, op=None, left=None, right=None, operand=None):
        self.type = type      # 'number', 'binop', or 'unary'
        self.value = value    # number value
        self.op = op          # operator: '+', '-', '*', '/'
        self.left = left      # left operand for binop
        self.right = right    # right operand for binop
        self.operand = operand # operand for unary
```

## Parser (Class-Based)

```python
import re

class Parser:
    def __init__(self, text):
        self.tokens = re.findall(r'\d+\.?\d*|[+\-*/()]', text.strip())
        self.pos = 0
    
    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def consume(self):
        token = self.tokens[self.pos]
        self.pos += 1
        return token
    
    def parse(self):
        result = self.parse_expression()
        return result
    
    # Lowest precedence: + and -
    def parse_expression(self):
        node = self.parse_term()
        while self.peek() in ('+', '-'):
            op = self.consume()
            right = self.parse_term()
            node = ASTNode('binop', op=op, left=node, right=right)
        return node
    
    # Higher precedence: * and /
    def parse_term(self):
        node = self.parse_unary()
        while self.peek() in ('*', '/'):
            op = self.consume()
            right = self.parse_unary()
            node = ASTNode('binop', op=op, left=node, right=right)
        return node
    
    # Unary minus (e.g., -5 or --3)
    def parse_unary(self):
        if self.peek() == '-':
            self.consume()
            operand = self.parse_unary()
            return ASTNode('unary', op='-', operand=operand)
        return self.parse_primary()
    
    # Numbers or parenthesized expressions
    def parse_primary(self):
        token = self.peek()
        if token == '(':
            self.consume()  # consume '('
            node = self.parse_expression()
            self.consume()  # consume ')'
            return node
        # Must be a number
        self.consume()
        return ASTNode('number', value=float(token))
```

## Evaluator

```python
def evaluate(node):
    if node.type == 'number':
        return node.value
    if node.type == 'unary':
        return -evaluate(node.operand)
    # binop: evaluate both sides, then apply operator
    left = evaluate(node.left)
    right = evaluate(node.right)
    if node.op == '+': return left + right
    if node.op == '-': return left - right
    if node.op == '*': return left * right
    if node.op == '/': return left / right
```

## Usage Example

```python
parser = Parser("2 + 3 * 4")
ast = parser.parse()
print(evaluate(ast))  # 14.0
```
