#
# A reimplementation of Julia's dllist
# https://github.com/JuliaLang/julia/blob/bed2cd540a11544ed4be381d471bbf590f0b745e/base/libdl.jl#L286-L290
#
# https://github.com/JuliaLang/julia/commit/cc7fc96c9f43773c017f06fb255723f00946d693

# maybe write in C and use meson?

import ctypes
from ctypes.util import find_library
import platform
from typing import List


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
            pass

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
            name = libc._dyld_get_image_name(i).decode('utf-8')
            if name:
                libraries.append(name)

        return libraries

# WINDOWS
# https://learn.microsoft.com/en-us/windows/win32/api/dbghelp/nf-dbghelp-enumerateloadedmodules64
elif platform.system().startswith('Windows'):
    # BOOL callback(PCSTR, ULONG, ULONG, PVOID
    ENUM_CALLBACK = ctypes.WINFUNCTYPE(ctypes.c_int32, ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.py_object))

    @ENUM_CALLBACK
    def enum_modules_callback(module_name, _module_base, _module_size, data):
        libraries = data.contents.value
        print(module_name, _module_base, _module_size)

        try:
            name = module_name.decode('utf-8')
            if name:
                libraries.append(name)
        except:
            pass
        return int(True)


    def _platform_specific_dllist() -> List[str]:
        # could have issues on WINE
        # see https://github.com/JuliaLang/julia/pull/33062
        libraries = []
        process = ctypes.windll.kernel32.GetCurrentProcess()
        print(process)
        enumerate_loaded_modules = ctypes.windll.dbghelp.EnumerateLoadedModules64
        enumerate_loaded_modules.argtypes = [ctypes.c_int32, ENUM_CALLBACK, ctypes.POINTER(ctypes.py_object)]
        print(enumerate_loaded_modules(process, enum_modules_callback, ctypes.pointer(ctypes.py_object(libraries))))

        return libraries

def dllist() -> List[str]:
    return _platform_specific_dllist()


if __name__ == '__main__':
    print(dllist())
