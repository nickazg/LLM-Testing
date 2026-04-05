"""Mock Houdini hou module for SOP network testing."""
from hou._mock import MockNode, _ROOT, _CALL_LOG


def node(path: str):
    """Get a node by path. Returns the root /obj node or traverses."""
    parts = [p for p in path.strip("/").split("/") if p]
    current = _ROOT
    for part in parts:
        found = None
        for child in current._children:
            if child._name == part:
                found = child
                break
        if found is None:
            return None
        current = found
    _CALL_LOG.append(("hou.node", path))
    return current


def _get_call_log():
    """Return the recorded call log for validation."""
    return list(_CALL_LOG)


def _get_all_nodes():
    """Return all nodes created during the session."""
    nodes = []
    def _walk(n):
        nodes.append(n)
        for c in n._children:
            _walk(c)
    _walk(_ROOT)
    return nodes
