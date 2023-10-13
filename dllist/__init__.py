"""A reimplementation of Julia's dllist"""

import platform
from typing import List

__version__ = "1.0.0"

_system = platform.system()
if _system.startswith("Linux"):
    from .linux import _platform_specific_dllist
elif _system.startswith("Darwin"):
    from .macos import _platform_specific_dllist
elif _system.startswith("Windows"):
    from .windows import _platform_specific_dllist
else:
    import warnings

    def _platform_specific_dllist() -> List[str]:
        warnings.warn(f"Unsupported platform {_system}")
        return []


def dllist() -> List[str]:
    """
    List the dynamic libraries loaded by the current process.

    This is a wrapper for platform-specific APIs on Windows, Linux, and macOS.
    On other platforms, this function will return an empty list.

    Returns
    -------
    List[str]
        The names of the dynamic libraries loaded by the current process.
    """
    return _platform_specific_dllist()
