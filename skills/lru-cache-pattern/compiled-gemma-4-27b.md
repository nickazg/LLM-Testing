# LRU Cache — HashMap + Doubly Linked List

## Rules

- Do NOT use `OrderedDict` — implement with dict + linked list
- `get` returns `-1` if key not found
- `put` overwrites existing keys (remove old, add new)
- MRU = front (after head), LRU = back (before tail)
