# 4. Sync and finalize

## Complete Pattern

```python
import hou

obj = hou.node("/obj")
topnet = obj.createNode("topnet")

processor = topnet.createNode("pythonprocessor")
processor.parm("generate").set("""
for i, path in enumerate(["file1.exr", "file2.exr", "file3.exr"]):
    item = item_holder.addWorkItem()
    item.setStringAttrib("filepath", path)
    item.setIntAttrib("batch", i // 2)
""")

partition = topnet.createNode("partitionbyattribute")
partition.parm("partitionattrib").set("batch")
partition.setInput(0, processor)

script = topnet.createNode("pythonscript")
script.parm("cook").set("""
filepath = self.work_item.attrib("filepath")
print(f"Processing: {filepath}")
""")
script.setInput(0, partition)

waitforall = topnet.createNode("waitforall")
waitforall.setInput(0, script)
waitforall.setDisplayFlag(True)
topnet.layoutChildren()
```

## Node Types

| Node | Purpose |
|------|---------|
| `pythonprocessor` | Generate work items with attributes |
| `partitionbyattribute` | Group items by attribute value |
| `pythonscript` | Run Python per work item |
| `waitforall` | Synchronize completion |

## Callback Contexts

**Python Processor (`generate` callback):**
- `item_holder.addWorkItem()` → creates a work item
- `item.setStringAttrib("name", value)` 
- `item.setIntAttrib("name", value)`

**Python Script (`cook` callback):**
- `self.work_item.attrib("name")` → read attribute value

## Node Operations

```python
node.setInput(0, upstream_node)  # Connect nodes
node.setDisplayFlag(True)         # Set display flag
topnet.layoutChildren()           # Auto-layout
```
