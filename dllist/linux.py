import ctypes
import warnings
from ctypes.util import find_library
from typing import List

# https://man7.org/linux/man-pages/man3/dl_iterate_phdr.3.html


class dl_phdr_info(ctypes.Structure):
    _fields_ = [
        ("dlpi_addr", ctypes.c_void_p),
        ("dlpi_name", ctypes.c_char_p),
        ("dlpi_phdr", ctypes.c_void_p),
        ("dlpi_phnum", ctypes.c_ushort),
    ]


@ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.POINTER(dl_phdr_info),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.py_object),
)
def info_callback(info, _size, data):
    libraries = data.contents.value
    try:
        name = info.contents.dlpi_name.decode("utf-8")
        libraries.append(name)
    except:
        warnings.warn(f"Could not decode library name {info.contents.dlpi_name}")

    return 0


def _platform_specific_dllist() -> List[str]:
    libraries: List[str] = []
    libc = ctypes.CDLL(find_library("c"))
    libc.dl_iterate_phdr(info_callback, ctypes.byref(ctypes.py_object(libraries)))

    if libraries:
        # remove the first entry, which is the executable itself
        libraries.pop(0)

    return libraries
