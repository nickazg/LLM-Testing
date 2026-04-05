"""Internal mock implementation for hou module."""

_CALL_LOG = []


class MockParm:
    """Mock for hou.Parm — tracks parameter sets."""

    def __init__(self, name: str, node_path: str):
        self._name = name
        self._node_path = node_path
        self._value = None

    def set(self, value):
        self._value = value
        _CALL_LOG.append(("parm.set", self._node_path, self._name, value))

    def eval(self):
        return self._value


class MockParmTuple:
    """Mock for hou.ParmTuple."""

    def __init__(self, name: str, node_path: str, size: int = 3):
        self._parms = [MockParm(f"{name}{i}", node_path) for i in range(size)]
        self._name = name

    def set(self, values):
        for p, v in zip(self._parms, values):
            p.set(v)

    def __getitem__(self, idx):
        return self._parms[idx]


class MockNode:
    """Mock for hou.Node — tracks creation, connections, flags."""

    def __init__(self, node_type: str, name: str, parent=None):
        self._type = node_type
        self._name = name
        self._parent = parent
        self._children = []
        self._inputs = {}
        self._parms = {}
        self._display_flag = False
        self._render_flag = False
        self._path = self._compute_path()

    def _compute_path(self):
        if self._parent is None:
            return "/"
        parent_path = self._parent._path
        if parent_path == "/":
            return f"/{self._name}"
        return f"{parent_path}/{self._name}"

    def createNode(self, node_type: str, name: str = None):
        if name is None:
            name = node_type + "1"
        child = MockNode(node_type, name, parent=self)
        self._children.append(child)
        _CALL_LOG.append(("createNode", self._path, node_type, name))
        return child

    def setInput(self, input_idx: int, source_node, output_idx: int = 0):
        self._inputs[input_idx] = (source_node, output_idx)
        _CALL_LOG.append(("setInput", self._path, input_idx, source_node._path))

    def parm(self, name: str):
        if name not in self._parms:
            self._parms[name] = MockParm(name, self._path)
        return self._parms[name]

    def parmTuple(self, name: str):
        if name not in self._parms:
            self._parms[name] = MockParmTuple(name, self._path)
        return self._parms[name]

    def setDisplayFlag(self, val: bool):
        self._display_flag = val
        _CALL_LOG.append(("setDisplayFlag", self._path, val))

    def setRenderFlag(self, val: bool):
        self._render_flag = val
        _CALL_LOG.append(("setRenderFlag", self._path, val))

    def layoutChildren(self):
        _CALL_LOG.append(("layoutChildren", self._path))

    def path(self):
        return self._path

    def name(self):
        return self._name

    def type(self):
        return type('NodeType', (), {'name': lambda s: self._type})()

    def children(self):
        return list(self._children)

    def inputs(self):
        return [self._inputs.get(i, (None, 0))[0] for i in range(max(self._inputs.keys()) + 1)] if self._inputs else []

    def node(self, relative_path: str):
        parts = [p for p in relative_path.strip("/").split("/") if p]
        current = self
        for part in parts:
            found = None
            for child in current._children:
                if child._name == part:
                    found = child
                    break
            if found is None:
                return None
            current = found
        return current


# Root of the node tree — /obj is pre-created
_ROOT_ROOT = MockNode("root", "")  # represents /
_OBJ = MockNode("obj", "obj", parent=_ROOT_ROOT)
_ROOT_ROOT._children.append(_OBJ)
_ROOT = _ROOT_ROOT
