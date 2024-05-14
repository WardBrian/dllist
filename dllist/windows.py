import ctypes
import warnings
from ctypes import wintypes
from typing import List, Optional

# https://learn.microsoft.com/windows/win32/api/psapi/nf-psapi-enumprocessmodules
# https://learn.microsoft.com/windows/win32/api/libloaderapi/nf-libloaderapi-getmodulefilenamew

_kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
_psapi = ctypes.WinDLL('psapi', use_last_error=True)

_kernel32.GetCurrentProcess.restype = wintypes.HANDLE

_kernel32.GetModuleFileNameW.restype = wintypes.DWORD
_kernel32.GetModuleFileNameW.argtypes = (
    wintypes.HMODULE,
    wintypes.LPWSTR,
    wintypes.DWORD,
)

_psapi.EnumProcessModules.restype = wintypes.BOOL
_psapi.EnumProcessModules.argtypes = (
    wintypes.HANDLE,
    ctypes.POINTER(wintypes.HMODULE),
    wintypes.DWORD,
    wintypes.LPDWORD,
)

def get_module_filename(hModule: wintypes.HMODULE) -> Optional[str]:
    name = (wintypes.WCHAR * 32767)() # UNICODE_STRING_MAX_CHARS
    if _kernel32.GetModuleFileNameW(hModule, name, len(name)):
        return name.value
    error = ctypes.get_last_error()
    warnings.warn(f"Failed to get module file name for module {hModule}: "
                  f"GetModuleFileNameW failed with error code {error}",
                  stacklevel=2)
    return None


def get_module_handles() -> List[int]:
    hProcess = _kernel32.GetCurrentProcess()
    cbNeeded = wintypes.DWORD()
    n = 1024
    while True:
        modules = (wintypes.HMODULE * n)()
        if not _psapi.EnumProcessModules(hProcess,
                                         modules,
                                         ctypes.sizeof(modules),
                                         ctypes.byref(cbNeeded)):
            break
        n = cbNeeded.value // ctypes.sizeof(wintypes.HMODULE)
        if n <= len(modules):
            return modules[:n]
    error = ctypes.get_last_error()
    warnings.warn("Unable to list loaded libraries: EnumProcessModules "
                  f"failed with error code {error}",
                  stacklevel=2)
    return []


def _platform_specific_dllist() -> List[str]:
    # skip first entry, which is the executable itself
    modules = get_module_handles()[1:]
    libraries = [name for h in modules
                    if (name := get_module_filename(h)) is not None]
    return libraries
