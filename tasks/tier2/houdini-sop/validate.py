"""Validator for tier2-houdini-sop task."""
import json
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
script = workspace / "build_sop_network.py"

if not script.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0

tests_passed = 0
total_tests = 10

try:
    # Ensure the mock hou module is importable
    sys.path.insert(0, str(workspace))

    # Run the user's script in-process so mock state is shared
    script_code = script.read_text()
    exec(compile(script_code, str(script), "exec"), {"__name__": "__main__"})

    # Import the mock to inspect what happened
    import hou

    call_log = hou._get_call_log()
    all_nodes = hou._get_all_nodes()

    # Build lookup structures
    nodes_by_path = {n._path: n for n in all_nodes}
    calls_by_type = {}
    for entry in call_log:
        calls_by_type.setdefault(entry[0], []).append(entry)

    # Test 1: geo container created under /obj
    geo_node = None
    for n in all_nodes:
        if n._parent and n._parent._name == "obj" and n._type == "geo":
            geo_node = n
            break
    if geo_node:
        tests_passed += 1

    # Test 2: grid node created
    grid_node = None
    for n in all_nodes:
        if n._type == "grid":
            grid_node = n
            break
    if grid_node:
        tests_passed += 1

    # Test 3: mountain node created
    mountain_node = None
    for n in all_nodes:
        if n._type == "mountain":
            mountain_node = n
            break
    if mountain_node:
        tests_passed += 1

    # Test 4: color node created
    color_node = None
    for n in all_nodes:
        if n._type == "color":
            color_node = n
            break
    if color_node:
        tests_passed += 1

    # Test 5: null (OUT) node created
    null_node = None
    for n in all_nodes:
        if n._type == "null":
            null_node = n
            break
    if null_node:
        tests_passed += 1

    # Test 6: Connections exist (at least 3 setInput calls)
    set_input_calls = calls_by_type.get("setInput", [])
    if len(set_input_calls) >= 3:
        tests_passed += 1

    # Test 7: Grid parameters set (rows and cols)
    parm_sets = calls_by_type.get("parm.set", [])
    parm_names = [(entry[2], entry[3]) for entry in parm_sets]  # (name, value)
    if any(name == "rows" for name, _ in parm_names) and any(name == "cols" for name, _ in parm_names):
        tests_passed += 1

    # Test 8: Mountain height set
    if any(name == "height" for name, _ in parm_names):
        tests_passed += 1

    # Test 9: Display flag set on null node
    display_calls = calls_by_type.get("setDisplayFlag", [])
    if any(val is True for _, _, val in display_calls):
        tests_passed += 1

    # Test 10: layoutChildren called
    layout_calls = calls_by_type.get("layoutChildren", [])
    if layout_calls:
        tests_passed += 1

except Exception:
    pass

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.7 else 1)
