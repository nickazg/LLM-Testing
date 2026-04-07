# LRU Cache — Dictionary + Doubly-Linked List

## ⚠️ Do NOT Use OrderedDict

Implement from scratch using dict + doubly-linked list.

## Pattern: Dict for Lookup, Linked List for Order

- **Dict** (`cache`): O(1) key → Node lookup
- **Doubly-linked list**: O(1) insertion/removal, tracks recency
- **Front = most recent**, **Back = least recent**
- **Sentinel nodes** (dummy head/tail) eliminate edge cases

## Implementation

```python
class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node

        # Dummy head/tail (sentinels) avoid None checks
        self.head = Node()  # front (most recent)
        self.tail = Node()  # back (least recent)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        """Unlink node from list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node):
        """Insert node right after head."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        # 1. Check if exists
        if key not in self.cache:
            return -1
        # 2. Move to front (remove, then add)
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        # 1. Remove old node if key exists
        if key in self.cache:
            self._remove(self.cache[key])

        # 2. Create and add new node
        node = Node(key, value)
        self.cache[key] = node
        self._add_to_front(node)

        # 3. Evict LRU if over capacity
        if len(self.cache) > self.capacity:
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
```

## Rules

- `get()`: Return `-1` if missing, else move to front and return value
- `put()`: If key exists, remove old node first. Always check capacity after insert.
- Evict from back (`tail.prev`), add to front (`head.next`)
