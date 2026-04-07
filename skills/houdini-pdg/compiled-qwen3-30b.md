# Houdini PDG/TOPs — Minimal Reference

## Setup

```python
import hou
obj = hou.node("/obj")
topnet = obj.createNode("topnet")
```

## Python Processor — Generate Work Items

```python
processor = topnet.createNode("pythonprocessor")
processor.parm("generate").set("""
for i, path in enumerate(["file1.exr", "file2.exr", "file3.exr"]):
    item = item_holder.addWorkItem()
    item.setStringAttrib("filepath", path)
    item.setIntAttrib("batch", i // 2)
""")
```

**Inside `generate` callback:** `item_holder.addWorkItem()` creates items. Use `item.setStringAttrib()`, `item.setIntAttrib()`, `item.setFloatAttrib()` to set attributes.

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

**Inside `cook` callback:** `self.work_item.attrib("name")` reads attributes.

## Finish

```python
waitforall = topnet.createNode("waitforall")
waitforall.setInput(0, script)
waitforall.setDisplayFlag(True)
topnet.layoutChildren()
```

**Connection pattern:** `downstream_node.setInput(0, upstream_node)`
