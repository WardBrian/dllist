# A reimplementation of Julia's dllist

import ctypes
from ctypes.util import find_library
import platform
from typing import List
import warnings


# LINUX/BSD (non-apple)
# https://man7.org/linux/man-pages/man3/dl_iterate_phdr.3.html

if platform.system().startswith('Linux'):
    class dl_phdr_info(ctypes.Structure):
        _fields_ = [
            ('dlpi_addr', ctypes.c_void_p),
            ('dlpi_name', ctypes.c_char_p),
            ('dlpi_phdr', ctypes.c_void_p),
            ('dlpi_phnum', ctypes.c_ushort),
        ]

    @ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(dl_phdr_info), ctypes.c_size_t, ctypes.POINTER(ctypes.py_object))
    def info_callback(info, _size, data):
        libraries = data.contents.value
        try:
            name = info.contents.dlpi_name.decode('utf-8')
            if name:
                libraries.append(name)
        except:
            warnings.warn(f'Could not decode library name {info.contents.dlpi_name}')

        return 0

    def _platform_specific_dllist() -> List[str]:
        libraries = []
        libc = ctypes.CDLL(find_library('c'))
        libc.dl_iterate_phdr(info_callback, ctypes.pointer(ctypes.py_object(libraries)))

        return libraries

# APPLE
# https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man3/dyld.3.html
elif platform.system().startswith('Darwin'):

    def _platform_specific_dllist() -> List[str]:
        libraries = []
        libc = ctypes.CDLL(find_library('c'))

        num_images = libc._dyld_image_count()

        get_image_name = libc._dyld_get_image_name
        get_image_name.restype = ctypes.c_char_p

        for i in range(num_images):
            raw_name =  libc._dyld_get_image_name(i)
            try:
                name = raw_name.decode('utf-8')
                if name:
                    libraries.append(name)
            except:
                warnings.warn(f'Could not decode library name {raw_name}')

        return libraries

# WINDOWS
# https://learn.microsoft.com/en-us/windows/win32/api/dbghelp/nf-dbghelp-enumerateloadedmodules64
elif platform.system().startswith('Windows'):


    LPVOID                          = ctypes.c_void_p
    PVOID                           = LPVOID
    HANDLE                          = LPVOID
    BOOL                            = ctypes.c_int32
    DWORD                           = ctypes.c_uint32
    PCSTR                           = ctypes.c_char_p
    ULONG                           = ctypes.c_uint32
    PENUMLOADED_MODULES_CALLBACK64  = ctypes.WINFUNCTYPE(BOOL, PCSTR, ULONG, ULONG, ctypes.POINTER(ctypes.py_object))

    @PENUMLOADED_MODULES_CALLBACK64
    def enum_modules_callback(module_name, _module_base, _module_size, data):
        libraries = data.contents.value

        try:
            name = module_name.decode('utf-8')
            if name:
                libraries.append(name)
        except:
            warnings.warn(f'Could not decode library name {module_name}')
        return int(True)


    def _platform_specific_dllist() -> List[str]:
        # could have issues on WINE
        # see https://github.com/JuliaLang/julia/pull/33062
        get_current_process = ctypes.windll.kernel32.GetCurrentProcess
        get_current_process.restype = HANDLE
        process = ctypes.windll.kernel32.GetCurrentProcess()

        libraries = []
        enumerate_loaded_modules = ctypes.windll.dbghelp.EnumerateLoadedModules64
        enumerate_loaded_modules.argtypes = [HANDLE, PENUMLOADED_MODULES_CALLBACK64 , ctypes.POINTER(ctypes.py_object)]
        success = enumerate_loaded_modules(process, enum_modules_callback, ctypes.pointer(ctypes.py_object(libraries)))
        if not success:
            warnings.warn(f'EnumerateLoadedModules64 failed with error code {ctypes.GetLastError()}')

        return libraries

else:
    def _platform_specific_dllist() -> List[str]:
        warnings.warn(f'Unsupported platform {platform.system()}')
        return []

def dllist() -> List[str]:
    return _platform_specific_dllist()


if __name__ == '__main__':
    print(dllist())
