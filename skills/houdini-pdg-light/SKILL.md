# Houdini PDG/TOPs — Key Patterns

- Create TOP network: `hou.node("/obj").createNode("topnet")`
- Inside topnet: `createNode("pythonprocessor")` for work item generation, `"partitionbyattribute"` for grouping, `"pythonscript"` for processing, `"waitforall"` for sync
- Connect nodes: `node.setInput(0, upstream_node)`
- Python Processor `generate` callback: `item = item_holder.addWorkItem()`, then `item.setStringAttrib("filepath", path)`, `item.setIntAttrib("batch", n)`
- Partition parm: `partition.parm("partitionattrib").set("batch")`
- Python Script `cook` callback: `filepath = self.work_item.attrib("filepath")`
- Display flag: `node.setDisplayFlag(True)`
- Layout: `topnet.layoutChildren()`
- Work item dependencies flow automatically through node connections
