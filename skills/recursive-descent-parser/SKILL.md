# Recursive Descent Expression Parser

## Grammar (EBNF)
```
expression = term (('+' | '-') term)*
term       = unary (('*' | '/') unary)*
unary      = '-' unary | primary
primary    = NUMBER | '(' expression ')'
NUMBER     = [0-9]+ ('.' [0-9]+)?
```

## ASTNode Structure
```python
class ASTNode:
    def __init__(self, type, value=None, op=None, left=None, right=None, operand=None):
        self.type = type        # 'number', 'binop', or 'unary'
        self.value = value      # float, for type='number'
        self.op = op            # str, for type='binop' or 'unary'
        self.left = left        # ASTNode, for type='binop'
        self.right = right      # ASTNode, for type='binop'
        self.operand = operand  # ASTNode, for type='unary'
```

## Parser Pattern (Tokenizer + Recursive Descent)
```python
import re

def parse(expression: str) -> ASTNode:
    tokens = re.findall(r'\d+\.?\d*|[+\-*/()]', expression.strip())
    if not tokens:
        raise ValueError("Empty expression")
    pos = [0]  # mutable index

    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def consume():
        token = tokens[pos[0]]
        pos[0] += 1
        return token

    def parse_expression():
        node = parse_term()
        while peek() in ('+', '-'):
            op = consume()
            right = parse_term()
            node = ASTNode('binop', op=op, left=node, right=right)
        return node

    def parse_term():
        node = parse_unary()
        while peek() in ('*', '/'):
            op = consume()
            right = parse_unary()
            node = ASTNode('binop', op=op, left=node, right=right)
        return node

    def parse_unary():
        if peek() == '-':
            consume()
            operand = parse_unary()
            return ASTNode('unary', op='-', operand=operand)
        return parse_primary()

    def parse_primary():
        token = peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        if token == '(':
            consume()
            node = parse_expression()
            if peek() != ')':
                raise ValueError("Unmatched parenthesis")
            consume()
            return node
        if re.match(r'\d', token):
            consume()
            return ASTNode('number', value=float(token))
        raise ValueError(f"Unexpected token: {token}")

    result = parse_expression()
    if pos[0] < len(tokens):
        raise ValueError("Unexpected tokens after expression")
    return result
```

## Evaluator
```python
def evaluate(node: ASTNode) -> float:
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
        if node.op == '/': return left / right  # raises ZeroDivisionError naturally
    raise ValueError(f"Unknown node type: {node.type}")
```
