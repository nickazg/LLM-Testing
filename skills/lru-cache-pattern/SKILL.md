# LRU Cache — Dict + Doubly-Linked List

## Node Structure
```python
class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None
```

## LRUCache with Sentinel Nodes
```python
import threading

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node
        self.lock = threading.Lock()
        # Sentinel nodes avoid edge cases
        self.head = Node()  # dummy head (most recent side)
        self.tail = Node()  # dummy tail (least recent side)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node):
        """Remove node from linked list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node: Node):
        """Add node right after head (most recently used)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key) -> any:
        with self.lock:
            if key not in self.cache:
                return -1
            node = self.cache[key]
            self._remove(node)
            self._add_to_front(node)
            return node.value

    def put(self, key, value) -> None:
        with self.lock:
            if key in self.cache:
                self._remove(self.cache[key])
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_front(node)
            if len(self.cache) > self.capacity:
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]

    def size(self) -> int:
        with self.lock:
            return len(self.cache)
```

## Key Points
- Do NOT use `collections.OrderedDict`
- Sentinel head/tail eliminate null checks
- `threading.Lock` wraps every public method
- `get()` returns `-1` for missing keys (not `None` — `None` is a valid value)
- `put()` overwrites if key exists (remove old node, add new)
