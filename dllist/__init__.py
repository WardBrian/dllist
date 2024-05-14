"""A reimplementation of Julia's dllist"""

import platform
import warnings
from typing import List

__version__ = "1.2.0"

_system = platform.system().lower()
if (
    _system.startswith("linux")
    or _system.startswith("freebsd")
    or _system.startswith("openbsd")
    or _system.startswith("sunos")
    or _system.startswith("solaris")
):
    from .unix_like import _platform_specific_dllist
elif _system.startswith("darwin"):
    from .macos import _platform_specific_dllist
elif _system.startswith("windows"):
    from .windows import _platform_specific_dllist
else:

    def _platform_specific_dllist() -> List[str]:
        warnings.warn(
            f"Unable to list loaded libraries for unsupported platform {_system}"
        )
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
    try:
        return _platform_specific_dllist()
    except Exception as e:
        warnings.warn(
            f"Unable to list loaded libraries: {e}",
        )
        return []
