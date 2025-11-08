from __future__ import annotations
import importlib
import pkgutil
import sys
from types import ModuleType
from typing import Iterable

"""
edge_tools package root.

Provides package metadata and light-weight lazy-loading for submodules.
Keep this file minimal to make imports cheap.
"""


import importlib.metadata

__all__ = ["__version__", "get_version"]

# Try to obtain the installed distribution version; fall back to a default.
try:
    __version__ = importlib.metadata.version("edge_tools")
except Exception:
    __version__ = "0.0.0"


def get_version() -> str:
    """Return the package version."""
    return __version__


# Cache list of available top-level submodules (names only)
_package_paths = __path__  # type: ignore[attr-defined]
_available_submodules = {name for _, name, ispkg in pkgutil.iter_modules(_package_paths)}

def _import_submodule(name: str) -> ModuleType:
    """Import a submodule of this package and cache it in the package namespace."""
    fullname = f"{__name__}.{name}"
    module = importlib.import_module(fullname)
    setattr(sys.modules[__name__], name, module)
    return module

def __getattr__(name: str):
    """
    Lazy-load submodules on attribute access.

    Example:
        from edge_tools import utilities  # loads edge_tools.utilities on first access
    """
    if name in _available_submodules:
        return _import_submodule(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def __dir__() -> Iterable[str]:
    """List public attributes including discovered submodules."""
    public = set(globals().keys()) | _available_submodules
    return sorted(public)