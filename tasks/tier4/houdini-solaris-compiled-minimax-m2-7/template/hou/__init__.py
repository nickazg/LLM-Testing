"""Mock Houdini hou module for Solaris/LOP testing.

Key difference from SOP mock: pwd().editableStage() returns a real
Usd.Stage.CreateInMemory() so validators can inspect actual USD content.
"""
from pxr import Usd

_STAGE = Usd.Stage.CreateInMemory()
_CALL_LOG = []


class _MockPwd:
    """Mock for the current node (hou.pwd()) in a Python Script LOP."""

    def editableStage(self):
        _CALL_LOG.append(("editableStage",))
        return _STAGE


_PWD = _MockPwd()


def pwd():
    """Return the current node mock (provides editableStage())."""
    return _PWD


def _get_stage():
    """Return the USD stage for validation."""
    return _STAGE


def _get_call_log():
    """Return recorded call log."""
    return list(_CALL_LOG)
