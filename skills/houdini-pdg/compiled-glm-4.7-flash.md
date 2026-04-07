# Wait for All — synchronization

## Quick Reference

| Operation | Code |
|-----------|------|
| Create TOP network | `topnet = hou.node("/obj").createNode("topnet")` |
| Create node | `node = topnet.createNode("nodetype")` |
| Set parameter | `node.parm("name").set("value")` |
| Connect nodes | `downstream.setInput(0, upstream)` |
| Set display flag | `node.setDisplayFlag(True)` |
| Layout network | `topnet.layoutChildren()` |

## Node Types

| Type | Purpose | Key Parameter |
|------|---------|---------------|
| `pythonprocessor` | Generate work items | `"generate"` callback |
| `partitionbyattribute` | Group by attribute | `"partitionattrib"` = attribute name |
| `pythonscript` | Process items | `"cook"` callback |
| `waitforall` | Sync all upstream | — |

## Work Item Attributes

```python
item = item_holder.addWorkItem()
item.setStringAttrib("name", value)
item.setIntAttrib("name", value)

value = self.work_item.attrib("name")
```

## Complete Example

```python
import hou

obj = hou.node("/obj")
topnet = obj.createNode("topnet")

processor = topnet.createNode("pythonprocessor")
processor.parm("generate").set("""
for i, path in enumerate(["file1.exr", "file2.exr", "file3.exr", "file4.exr", "file5.exr"]):
    item = item_holder.addWorkItem()
    item.setStringAttrib("filepath", path)
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
