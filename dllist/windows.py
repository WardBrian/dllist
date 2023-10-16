import ctypes
import warnings
from ctypes.wintypes import BOOL, DWORD, HANDLE, HMODULE, LPDWORD, LPWSTR
from typing import List, Optional, Sequence, Tuple

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
    try:
        lpFilename = ctypes.create_unicode_buffer(nSize)
        if _get_module_filename(hModule, lpFilename, nSize) != 0:
            return lpFilename.value
        else:
            warnings.warn(
                f"Failed to get module file name for module {hModule}", stacklevel=2
            )
    except:
        warnings.warn(
            f"Failed to get module file name for module {hModule}", stacklevel=2
        )
    return None


def get_process_module_handles_partial(
    hProcess: HANDLE, maxbuffsize: int
) -> Tuple[Sequence[HMODULE], int]:
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
        ctypes.byref(cbNeeded),
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


def get_process_module_handles() -> Sequence[HMODULE]:
    hProcess = get_current_process()
    first_attempt = 1024
    hModules, buffer_needed = get_process_module_handles_partial(
        hProcess, maxbuffsize=first_attempt
    )
    if buffer_needed > first_attempt:
        # We need a bigger buffer, but luckily we know how big it needs to be
        hModules, buffer_needed = get_process_module_handles_partial(
            hProcess, maxbuffsize=buffer_needed
        )

    # skip first entry, which is the executable itself,
    # and trim the list to the number of modules actually loaded
    return hModules[1:buffer_needed]


def _platform_specific_dllist() -> List[str]:
    hModules = get_process_module_handles()

    libraries = [
        name for hMod in hModules if (name := get_module_filename(hMod)) is not None
    ]

    return libraries
