from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        name="cython_mod.gate_ops",          # package.module
        sources=["cython_mod/gate_ops.pyx"], # path to .pyx
    )
]

setup(
    name="cython_mod",
    ext_modules=cythonize(
        extensions,
        compiler_directives={"language_level": "3"},
    ),
)
