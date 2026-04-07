"""Validator for tier3-expression-parser task."""
import json
import sys
import math
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
parser_py = workspace / "expr_parser.py"

if not parser_py.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0

sys.path.insert(0, str(workspace))
tests_passed = 0
total_tests = 20

try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("expr_parser", str(parser_py))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    parse = mod.parse
    evaluate = mod.evaluate

    def check(expr, expected):
        global tests_passed
        try:
            tree = parse(expr)
            result = evaluate(tree)
            if abs(result - expected) < 1e-9:
                tests_passed += 1
                return True
        except Exception:
            pass
        return False

    # Basic arithmetic (tests 1-4)
    check("2 + 3", 5.0)
    check("10 - 4", 6.0)
    check("3 * 7", 21.0)
    check("20 / 4", 5.0)

    # Precedence (tests 5-7)
    check("2 + 3 * 4", 14.0)
    check("10 - 2 * 3", 4.0)
    check("2 * 3 + 4 * 5", 26.0)

    # Parentheses (tests 8-10)
    check("(2 + 3) * 4", 20.0)
    check("((1 + 2) * (3 + 4))", 21.0)
    check("(10 - (3 + 2)) * 2", 10.0)

    # Unary minus (tests 11-13)
    check("-5", -5.0)
    check("-5 + 3", -2.0)
    check("-(3 + 2)", -5.0)

    # Complex expressions (tests 14-16)
    check("1 + 2 * 3 - 4 / 2", 5.0)
    check("(1 + 2) * (3 - 4) / (5 + 1)", -0.5)
    check("3.14 * 2", 6.28)

    # Single number (test 17)
    check("42", 42.0)

    # Error cases (tests 18-20)
    # Test 18: Invalid expression raises ValueError
    try:
        parse("")
        # Should have raised
    except ValueError:
        tests_passed += 1
    except Exception:
        pass

    # Test 19: Unmatched parens
    try:
        parse("(2 + 3")
        # Should have raised
    except ValueError:
        tests_passed += 1
    except Exception:
        pass

    # Test 20: Division by zero
    try:
        tree = parse("1 / 0")
        evaluate(tree)
        # Should have raised
    except ZeroDivisionError:
        tests_passed += 1
    except Exception:
        pass

except Exception:
    pass

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.8 else 1)
