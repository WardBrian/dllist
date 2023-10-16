import platform

import pytest

from dllist import dllist

if not platform.system().startswith("Darwin"):
    pytest.skip(reason="macOS only", allow_module_level=True)


def test_dllist_basic():
    dlls = dllist()
    print()
    print("\n".join(dlls))
    assert len(dlls) > 0
    assert any("libSystem.B.dylib" in dll for dll in dlls)

def test_euler():
    dlls = dllist()
    num_dlls = len(dlls)

    euler = pytest.importorskip("euler")

    dlls2 = dllist()
    print(dlls2)
    assert len(dlls2) > num_dlls
    assert any("/dllist/test/test_ext/euler.cpython" in dll for dll in dlls2)
