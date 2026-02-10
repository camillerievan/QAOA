from setuptools import setup
from Cython.Build import cythonize

setup(
    name="fast_sre",
    ext_modules=cythonize(
        "gate_ops.pyx",
        compiler_directives={"language_level": "3"},
    ),
)
