"""Validator for tier3-lru-cache task."""
import json
import sys
import threading
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
cache_py = workspace / "lru_cache.py"

if not cache_py.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0

# Import the module
sys.path.insert(0, str(workspace))
tests_passed = 0
total_tests = 15

try:
    import importlib
    spec = importlib.util.spec_from_file_location("lru_cache", str(cache_py))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    LRUCache = mod.LRUCache

    # Test 1: Basic put and get
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    if c.get(1) == 1:
        tests_passed += 1

    # Test 2: Eviction on capacity
    c.put(3, 3)  # evicts key 2
    if c.get(2) == -1:
        tests_passed += 1

    # Test 3: Key 1 survives (was accessed)
    if c.get(1) == 1:
        tests_passed += 1

    # Test 4: Overwrite existing key
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    c.put(1, 10)  # update value
    if c.get(1) == 10:
        tests_passed += 1

    # Test 5: Overwrite doesn't increase size
    c.put(3, 3)  # should evict 2, not 1
    if c.get(2) == -1 and c.get(1) == 10:
        tests_passed += 1

    # Test 6: Get non-existent key
    c = LRUCache(1)
    if c.get(99) == -1:
        tests_passed += 1

    # Test 7: Capacity 1
    c = LRUCache(1)
    c.put(1, 1)
    c.put(2, 2)
    if c.get(1) == -1 and c.get(2) == 2:
        tests_passed += 1

    # Test 8: LRU ordering with multiple accesses
    c = LRUCache(3)
    c.put(1, 1)
    c.put(2, 2)
    c.put(3, 3)
    c.get(1)  # access 1, LRU order: 2, 3, 1
    c.put(4, 4)  # evicts 2
    if c.get(2) == -1 and c.get(1) == 1:
        tests_passed += 1

    # Test 9: size() method
    c = LRUCache(3)
    c.put(1, 1)
    c.put(2, 2)
    if hasattr(c, 'size') and c.size() == 2:
        tests_passed += 1

    # Test 10: size after eviction
    c.put(3, 3)
    c.put(4, 4)  # evicts 1
    if hasattr(c, 'size') and c.size() == 3:
        tests_passed += 1

    # Test 11: Empty cache
    c = LRUCache(5)
    if hasattr(c, 'size') and c.size() == 0:
        tests_passed += 1

    # Test 12: String keys and values
    c = LRUCache(2)
    c.put("a", "hello")
    c.put("b", "world")
    if c.get("a") == "hello":
        tests_passed += 1

    # Test 13: None values
    c = LRUCache(2)
    c.put(1, None)
    # This is tricky — get returns -1 for missing, but None is a valid value
    # We test that the key exists by checking it doesn't return -1
    result = c.get(1)
    if result is None:
        tests_passed += 1

    # Test 14: Does NOT use OrderedDict
    import inspect
    source = inspect.getsource(mod.LRUCache)
    if "OrderedDict" not in source:
        tests_passed += 1

    # Test 15: Thread safety — concurrent operations don't crash
    c = LRUCache(100)
    errors = []
    def writer(start):
        try:
            for i in range(start, start + 50):
                c.put(i, i * 10)
        except Exception as e:
            errors.append(e)
    def reader(start):
        try:
            for i in range(start, start + 50):
                c.get(i)
        except Exception as e:
            errors.append(e)

    threads = []
    for i in range(4):
        threads.append(threading.Thread(target=writer, args=(i * 50,)))
        threads.append(threading.Thread(target=reader, args=(i * 50,)))
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)
    if not errors:
        tests_passed += 1

except Exception:
    pass

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.8 else 1)
