import ctypes
import warnings
from ctypes.wintypes import BOOL, DWORD, HANDLE, HMODULE, LPDWORD, LPWSTR
from typing import List, Optional, Tuple

# https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-enumprocessmodulesex

LIST_MODULES_ALL = 3  # 0x03


def get_current_process() -> HANDLE:
    _get_current_process = ctypes.windll.kernel32.GetCurrentProcess
    _get_current_process.restype = HANDLE
    return _get_current_process()


def get_module_filename(hModule: HMODULE) -> Optional[str]:
    _get_module_filename = ctypes.windll.kernel32.GetModuleFileNameW
    _get_module_filename.argtypes = [HMODULE, LPWSTR, DWORD]
    _get_module_filename.restype = DWORD

    nSize = 32768  # MAX_PATH
    lpFilename = ctypes.create_unicode_buffer(nSize)
    if _get_module_filename(hModule, lpFilename, nSize) != 0:
        # encoding?
        return lpFilename.value
    else:
        warnings.warn(
            f"Failed to get module file name for module {hModule}", stacklevel=2
        )


def get_process_module_handles_partial(
    hProcess: HANDLE, maxbuffsize: int
) -> Tuple[List[HMODULE], int]:
    _enumerate_loaded_modules = ctypes.windll.psapi.EnumProcessModulesEx
    _enumerate_loaded_modules.argtypes = [
        HANDLE,
        ctypes.POINTER(HMODULE),
        DWORD,
        LPDWORD,
        DWORD,
    ]
    _enumerate_loaded_modules.restype = BOOL
    cb = DWORD(maxbuffsize * ctypes.sizeof(HMODULE))
    cbNeeded = DWORD(0)

    hModules = (HMODULE * maxbuffsize)()
    success = _enumerate_loaded_modules(
        hProcess,
        hModules,
        cb,
        ctypes.pointer(cbNeeded),
        LIST_MODULES_ALL,
    )

    if not success:
        warnings.warn(
            "Unable to list loaded libraries: "
            f"EnumProcessModulesEx failed with error code {ctypes.GetLastError()}",
            stacklevel=3,
        )
        return [], 0

    bufsize_needed = cbNeeded.value // ctypes.sizeof(HMODULE)

    return hModules, bufsize_needed


def get_process_module_handles() -> List[HMODULE]:
    hProcess = get_current_process()
    hModules, cb_needed = get_process_module_handles_partial(hProcess, maxbuffsize=1024)
    if cb_needed > 1024:
        # retry with larger buffer
        hModules, _ = get_process_module_handles_partial(
            hProcess, maxbuffsize=cb_needed
        )
    return hModules


def _platform_specific_dllist() -> List[str]:
    hModules = get_process_module_handles()

    libraries = [
        name for hMod in hModules if (name := get_module_filename(hMod)) is not None
    ]

    if libraries:
        # remove the first entry, which is the executable itself
        libraries.pop(0)

    return libraries
