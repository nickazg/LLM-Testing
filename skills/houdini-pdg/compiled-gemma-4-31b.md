# 5. Finalize

## Core Pattern

```python
import hou

obj = hou.node("/obj")
topnet = obj.createNode("topnet")

node = topnet.createNode("nodetype")
node.parm("parmname").set("value")
downstream.setInput(0, upstream)

final_node.setDisplayFlag(True)
topnet.layoutChildren()
```

## Node Types

| Node | Purpose |
|------|---------|
| `pythonprocessor` | Generate work items |
| `partitionbyattribute` | Group items by attribute |
| `pythonscript` | Process each item |
| `waitforall` | Sync upstream items |

## Python Processor — Generate Items

```python
processor = topnet.createNode("pythonprocessor")
processor.parm("generate").set("""
for i, path in enumerate(["file1.exr", "file2.exr", "file3.exr", "file4.exr", "file5.exr"]):
    item = item_holder.addWorkItem()
    item.setStringAttrib("filepath", path)
    item.setIntAttrib("batch", i // 3)
""")
```

**Key**: Inside callback, use `item_holder.addWorkItem()` to create items, then call attribute setters on the returned item:
- `item.setStringAttrib("name", value)`
- `item.setIntAttrib("name", value)`

## Partition by Attribute

```python
partition = topnet.createNode("partitionbyattribute")
partition.parm("partitionattrib").set("batch")
partition.setInput(0, processor)
```

## Python Script — Process Items

```python
script = topnet.createNode("pythonscript")
script.parm("cook").set("""
filepath = self.work_item.attrib("filepath")
print(f"Processing: {filepath}")
""")
script.setInput(0, partition)
```

**Key**: Inside callback, use `self.work_item.attrib("name")` to read attributes.

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
