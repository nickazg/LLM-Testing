# 4. Sync and finalize

## Complete Template

```python
import hou

obj = hou.node("/obj")
topnet = obj.createNode("topnet")

processor = topnet.createNode("pythonprocessor")
processor.parm("generate").set("""
for i in range(5):
    item = item_holder.addWorkItem()
    item.setStringAttrib("filepath", f"file{i}.exr")
    item.setIntAttrib("batch", i // 3)
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

| Node Type | Purpose |
|-----------|---------|
| `topnet` | Container for TOP nodes |
| `pythonprocessor` | Generate work items programmatically |
| `partitionbyattribute` | Group items by attribute value |
| `pythonscript` | Execute Python per work item |
| `waitforall` | Wait for upstream completion |

## Key Callbacks

**Python Processor** (`generate` callback):
- `item_holder.addWorkItem()` → creates a work item
- `item.setStringAttrib("name", value)`
- `item.setIntAttrib("name", value)`

**Python Script** (`cook` callback):
- `self.work_item.attrib("name")` → read attribute value

## Connections

```python
downstream_node.setInput(0, upstream_node)
```
