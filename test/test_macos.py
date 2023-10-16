import platform

import pytest

if not platform.system().startswith("Darwin"):
    pytest.skip(reason="macOS only", allow_module_level=True)


from test import print_list

from dllist import dllist


def test_dllist_basic() -> None:
    dlls = dllist()
    print_list(dlls)
    assert len(dlls) > 0
    assert any("libSystem.B.dylib" in dll for dll in dlls)


def test_euler() -> None:
    dlls = dllist()
    num_dlls = len(dlls)

    euler = pytest.importorskip("euler")

    dlls2 = dllist()
    print_list(dlls2)

    assert len(dlls2) > num_dlls
    assert any("/dllist/test/test_éxt/euler.cpython" in dll for dll in dlls2)
