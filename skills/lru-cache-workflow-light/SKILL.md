# LRU Cache — Approach & Guardrails

## Approach
Build an LRU (Least Recently Used) cache with O(1) time complexity for both get and put operations. Use a hash map for O(1) lookup combined with a doubly-linked list for O(1) insertion/removal ordering.

## Key Guardrails

- **O(1) is non-negotiable** — both get() and put() must be constant time. If you're iterating to find the least-recently-used item, your design is wrong.
- **Thread safety matters** — use a lock to protect concurrent access. Consider that eviction and insertion can race.
- **Duplicate key overwrites** — when put() is called with an existing key, update the value AND move the node to most-recently-used position. Don't insert a second node.
- **Eviction order** — evict the LEAST recently used, not least frequently used. Any access (get or put) makes an item the most recent.
- **Don't use OrderedDict** — the constraint requires dict + linked list implementation.
- **Edge case: capacity** — handle capacity of 0 or 1 gracefully.
- **Return convention** — get() returns -1 for missing keys, not None or an exception.
