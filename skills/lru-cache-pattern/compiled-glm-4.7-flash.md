# LRU Cache — Dict + Doubly Linked List

## Node Class

```python
class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None
```

## LRUCache Class

```python
class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.cache = {}  # key -> Node
        
        # Dummy head and tail avoid null checks
        self.head = Node()  # most recent side
        self.tail = Node()  # least recent side
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        # Unlink node from list
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_front(self, node):
        # Insert right after head (most recent)
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self._remove(self.cache[key])
        
        node = Node(key, value)
        self.cache[key] = node
        self._add_front(node)
        
        # Evict LRU if over capacity
        if len(self.cache) > self.cap:
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
```

## Key Points

- **Head side** = most recently used, **Tail side** = least recently used
- Sentinel (dummy) nodes eliminate null/edge case checks
- `get()` returns `-1` for missing keys
- `put()` overwrites existing keys
- On access, always move node to front
