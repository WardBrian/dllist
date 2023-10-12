#
# A reimplementation of Julia's dllist
# https://github.com/JuliaLang/julia/blob/bed2cd540a11544ed4be381d471bbf590f0b745e/base/libdl.jl#L286-L290
#
# https://github.com/JuliaLang/julia/commit/cc7fc96c9f43773c017f06fb255723f00946d693
# https://learn.microsoft.com/en-us/windows/win32/api/dbghelp/nf-dbghelp-enumerateloadedmodules64

# maybe write in C and use meson?

import ctypes
from ctypes.util import find_library
import platform


# LINUX/BSD (non-apple)
# https://man7.org/linux/man-pages/man3/dl_iterate_phdr.3.html
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

# APPLE
# https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man3/dyld.3.html



def dlllist():
    libraries = []
    if platform.system().startswith('Linux'):
        lib = ctypes.CDLL(find_library('c'))
        lib.dl_iterate_phdr(info_callback, ctypes.pointer(ctypes.py_object(libraries)))
    elif platform.system().startswith('Darwin'):
        lib = ctypes.CDLL(find_library('c'))
        num_images = lib._dyld_image_count()
        get_image_name = lib._dyld_get_image_name
        get_image_name.restype = ctypes.c_char_p
        for i in range(num_images):
            name = lib._dyld_get_image_name(i).decode('utf-8')
            if name:
                libraries.append(name)
    elif platform.system().startswith('Windows'):
        # lib = ctypes.cdll.mscvrt
        # ctypes.CDLL(find_msvcrt())._get_dll_list(info_callback, ctypes.pointer(ctypes.py_object(libraries)))
        pass

    return libraries


if __name__ == '__main__':
    print(dlllist())
