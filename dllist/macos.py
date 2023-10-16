import ctypes
import warnings
from ctypes.util import find_library
from typing import List

# https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man3/dyld.3.html


def _platform_specific_dllist() -> List[str]:
    libraries = []
    libc = ctypes.CDLL(find_library("c"))

    num_images = libc._dyld_image_count()

    get_image_name = libc._dyld_get_image_name
    get_image_name.restype = ctypes.c_char_p

    # start at 1 to skip executable
    for i in range(1, num_images):
        raw_name = libc._dyld_get_image_name(i)
        try:
            name = raw_name.decode("utf-8")
            libraries.append(name)
        except:
            warnings.warn(f"Could not decode library name {raw_name}")

    return libraries
