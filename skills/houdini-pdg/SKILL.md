# Houdini PDG/TOPs Python API Reference

## Creating a TOP Network

TOP networks live under `/obj`. Create one from the obj context:

```python
import hou

obj = hou.node("/obj")
topnet = obj.createNode("topnet")
```

## Python Processor — Work Item Generation

The Python Processor node generates work items programmatically. Create it inside the topnet:

```python
processor = topnet.createNode("pythonprocessor")
```

### onGenerate Callback

Set the `onGenerate` callback to define how work items are created:

```python
processor.parm("generate").set("""
# 'self' is the node, 'item_holder' provides addWorkItem()
for i, path in enumerate(["file1.exr", "file2.exr", "file3.exr", "file4.exr", "file5.exr"]):
    item = item_holder.addWorkItem()
    item.setStringAttrib("filepath", path)
    item.setIntAttrib("batch", i // 3)
""")
```

Key objects in the callback:
- `item_holder` — the work item holder, call `item_holder.addWorkItem()` to create items
- `work_item` — a generated work item instance
- `work_item.setStringAttrib("name", value)` — set a string attribute
- `work_item.setIntAttrib("name", value)` — set an integer attribute
- `work_item.setFloatAttrib("name", value)` — set a float attribute

## Partition by Attribute

Groups work items by a shared attribute value:

```python
partition = topnet.createNode("partitionbyattribute")
partition.parm("partitionattrib").set("batch")
```

Work items with the same value of "batch" will be grouped into the same partition.

## Python Script — Processing Work Items

The Python Script node runs code on each work item during cook:

```python
script = topnet.createNode("pythonscript")
script.parm("cook").set("""
# Access the current work item's attributes
filepath = self.work_item.attrib("filepath")
print(f"Processing: {filepath}")
""")
```

In the `onCookTask` callback:
- `self.work_item` — the current work item being processed
- `self.work_item.attrib("name")` — read an attribute value
- `self.work_item.resultData` — output results

## Wait for All

Synchronization node — waits for all upstream work items to complete:

```python
waitforall = topnet.createNode("waitforall")
```

## Connecting Nodes

Connect nodes in sequence using `setInput(input_index, upstream_node)`:

```python
partition.setInput(0, processor)
script.setInput(0, partition)
waitforall.setInput(0, script)
```

Input index 0 is the primary input. Upstream work item dependencies are automatically established through connections.

## Display Flag and Layout

Set the display flag on the final node and lay out the network:

```python
waitforall.setDisplayFlag(True)
topnet.layoutChildren()
```

## Complete Example

```python
import hou

obj = hou.node("/obj")
topnet = obj.createNode("topnet")

# 1. Python Processor — generate work items
processor = topnet.createNode("pythonprocessor")
processor.parm("generate").set("""
for i, path in enumerate(["file1.exr", "file2.exr", "file3.exr", "file4.exr", "file5.exr"]):
    item = item_holder.addWorkItem()
    item.setStringAttrib("filepath", path)
    item.setIntAttrib("batch", i // 3)
""")

# 2. Partition by batch attribute
partition = topnet.createNode("partitionbyattribute")
partition.parm("partitionattrib").set("batch")
partition.setInput(0, processor)

# 3. Python Script — process each item
script = topnet.createNode("pythonscript")
script.parm("cook").set("""
filepath = self.work_item.attrib("filepath")
print(f"Processing: {filepath}")
""")
script.setInput(0, partition)

# 4. Wait for All
waitforall = topnet.createNode("waitforall")
waitforall.setInput(0, script)

# 5. Finalize
waitforall.setDisplayFlag(True)
topnet.layoutChildren()
```
