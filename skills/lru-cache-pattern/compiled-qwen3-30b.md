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

## LRUCache Implementation

```python
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # key -> Node
        
        # Dummy head and tail simplify edge cases
        self.head = Node()  # most recent side
        self.tail = Node()  # least recent side
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        # Bypass the node in the list
        left = node.prev
        right = node.next
        left.next = right
        right.prev = left

    def _add_to_front(self, node):
        # Insert right after head (most recent position)
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.cache:
            return -1
        node = self.cache[key]
        # Move accessed node to front
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key, value):
        # If key exists, remove old node first
        if key in self.cache:
            self._remove(self.cache[key])
        
        # Add new node
        new_node = Node(key, value)
        self.cache[key] = new_node
        self._add_to_front(new_node)
        
        # Evict LRU if over capacity
        if len(self.cache) > self.capacity:
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
```

## Key Points

- Do NOT use `collections.OrderedDict`
- Dummy head/tail nodes eliminate null/edge case checks
- Most recent = front (after head), Least recent = back (before tail)
- `get()` returns `-1` for missing keys
- `put()` updates existing keys and evicts LRU when over capacity
