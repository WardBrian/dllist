from distutils.core import Extension, setup

module1 = Extension("euler", sources=["euler.c"])

setup(
    name="euler",
    version="1.0",
    description="This is a demo package",
    ext_modules=[module1],
)
