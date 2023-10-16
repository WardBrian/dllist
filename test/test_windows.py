import platform

import pytest

from dllist import dllist

if not platform.system().startswith("Windows"):
    pytest.skip(reason="Windows only", allow_module_level=True)


def test_dllist_basic():
    dlls = dllist()
    print()
    print("\n".join(dlls))
    assert len(dlls) > 0
    assert any("kernel32.dll" in dll.lower() for dll in dlls)

def test_euler():
    dlls = dllist()
    num_dlls = len(dlls)

    euler = pytest.importorskip("euler")

    dlls2 = dllist()
    assert len(dlls2) > num_dlls
    assert any("\\dllist\\test\\test_éxt\\euler.cp" in dll.lower() for dll in dlls2)
