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
        self.capacity = capacity
        self.cache = {}  # key -> Node
        
        # Dummy head and tail (sentinel nodes eliminate edge cases)
        self.head = Node()  # most recent side
        self.tail = Node()  # least recent side
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        # Unlink node from the linked list
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node):
        # Insert node right after head (most recently used position)
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)        # remove from current position
        self._add_to_front(node)  # move to front (most recent)
        return node.value

    def put(self, key, value):
        if key in self.cache:
            self._remove(self.cache[key])  # remove old node
        
        node = Node(key, value)
        self.cache[key] = node
        self._add_to_front(node)
        
        # Evict LRU if over capacity
        if len(self.cache) > self.capacity:
            lru = self.tail.prev      # least recently used is at tail
            self._remove(lru)
            del self.cache[lru.key]
```

## Key Points

- **Sentinel nodes** (dummy head/tail) eliminate null checks and edge cases
- **Head side** = most recently used, **Tail side** = least recently used
- `get()` returns `-1` for missing keys (never returns `None`)
- `put()` overwrites existing keys (removes old node first, then adds new)
- Always move accessed/updated nodes to front (head side)
