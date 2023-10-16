# dllist

A very small Python library to list the DLLs loaded by the current process.
This is equivalent to the [`dllist`](https://docs.julialang.org/en/v1/stdlib/Libdl/#Base.Libc.Libdl.dllist) function in Julia.

*Note*: This library is intended to work on macOS, Linux, and Windows. Other platforms will return an empty list and raise a warning.

## Installation

`dllist` is [available on PyPI](https://pypi.org/project/dllist/):

```
pip install dllist
```

## Usage

```python
import dllist
print(dllist.dllist())
# ['linux-vdso.so.1', '/lib/x86_64-linux-gnu/libpthread.so.0', '/lib/x86_64-linux-gnu/libdl.so.2', ...
```

*Note*: The library paths are not postprocessed by this library. Depending on your usage, you may need to convert them to absolute paths and/or perform case-normalization (Windows).
