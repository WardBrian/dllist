import ctypes
import warnings
from typing import List

# https://learn.microsoft.com/en-us/windows/win32/api/dbghelp/nf-dbghelp-enumerateloadedmodules64

# fmt: off
LPVOID                          = ctypes.c_void_p
PVOID                           = LPVOID
HANDLE                          = LPVOID
BOOL                            = ctypes.c_int32
DWORD                           = ctypes.c_uint32
PCSTR                           = ctypes.c_char_p
ULONG                           = ctypes.c_uint32
PENUMLOADED_MODULES_CALLBACK64  = ctypes.WINFUNCTYPE(BOOL, PCSTR, ULONG, ULONG, ctypes.POINTER(ctypes.py_object))
# fmt: on


@PENUMLOADED_MODULES_CALLBACK64
def enum_modules_callback(module_name, _module_base, _module_size, data):
    libraries = data.contents.value

    try:
        name = module_name.decode("utf-8")
        if name:
            libraries.append(name)
    except:
        warnings.warn(f"Could not decode library name {module_name}")
    return int(True)


def _platform_specific_dllist() -> List[str]:
    # could have issues on WINE
    # see https://github.com/JuliaLang/julia/pull/33062
    get_current_process = ctypes.windll.kernel32.GetCurrentProcess
    get_current_process.restype = HANDLE
    process = ctypes.windll.kernel32.GetCurrentProcess()

    libraries = []
    enumerate_loaded_modules = ctypes.windll.dbghelp.EnumerateLoadedModules64
    enumerate_loaded_modules.argtypes = [
        HANDLE,
        PENUMLOADED_MODULES_CALLBACK64,
        ctypes.POINTER(ctypes.py_object),
    ]
    success = enumerate_loaded_modules(
        process, enum_modules_callback, ctypes.pointer(ctypes.py_object(libraries))
    )
    if not success:
        warnings.warn(
            f"EnumerateLoadedModules64 failed with error code {ctypes.GetLastError()}"
        )

    return libraries
