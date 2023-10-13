import platform

import pytest

from dllist import dllist

system = platform.system()


@pytest.mark.skipif(not system.startswith("Linux"), reason="Linux only")
def test_linux():
    dlls = dllist()
    print()
    print("\n".join(dlls))
    assert len(dlls) > 0
    assert any("libc.so" in dll for dll in dlls)


@pytest.mark.skipif(not system.startswith("Darwin"), reason="macOS only")
def test_macos():
    dlls = dllist()
    print()
    print("\n".join(dlls))
    assert len(dlls) > 0
    assert any("libSystem.B.dylib" in dll for dll in dlls)


@pytest.mark.skipif(not system.startswith("Windows"), reason="Windows only")
def test_windows():
    dlls = dllist()
    print()
    print("\n".join(dlls))
    assert len(dlls) > 0
    assert any("kernel32.dll" in dll.lower() for dll in dlls)


@pytest.mark.skipif(
    system.startswith("Linux")
    or system.startswith("Darwin")
    or system.startswith("Windows"),
    reason="Only runs on unknown platforms",
)
def test_unknown():
    with pytest.warns(UserWarning):
        dlls = dllist()
    assert len(dlls) == 0
