# dllist

A very small Python library to list the DLLs loaded by the current process.
This is equivalent to the [`dllist`](https://docs.julialang.org/en/v1/stdlib/Libdl/#Base.Libc.Libdl.dllist) function in Julia.

*Note*: This library is intended to work on macOS, Linux, and Windows. Other platforms will return an empty list and raise a warning.
