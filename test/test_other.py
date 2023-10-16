import platform

import pytest

from dllist import dllist

system = platform.system()

if (
    system.startswith("Linux")
    or system.startswith("Darwin")
    or system.startswith("Windows")
):
    pytest.skip(reason="Only runs on unknown platforms", allow_module_level=True)


def test_dllist_basic() -> None:
    with pytest.warns(UserWarning):
        dlls = dllist()
    assert len(dlls) == 0
