from __future__ import annotations

import os
import sys
from setuptools import Extension, setup, find_packages

try:
    from Cython.Build import cythonize
except Exception as e:  # pragma: no cover
    raise SystemExit("Cython is required to build this project. Install it with: pip install Cython") from e


def _openmp_flags():
    # Best-effort OpenMP flags; can be disabled with LAB10_OPENMP=0.
    if os.environ.get("LAB10_OPENMP", "1") == "0":
        return [], []

    if sys.platform.startswith("win"):
        # MSVC
        return ["/openmp"], []
    # GCC/Clang
    return ["-fopenmp"], ["-fopenmp"]


compile_args = ["-O3"]
link_args = []
omp_c, omp_l = _openmp_flags()
compile_args += omp_c
link_args += omp_l

ext_modules = [
    Extension(
        "lab10.integrate_cy",
        ["src/lab10/integrate_cy.pyx"],
        extra_compile_args=compile_args,
        extra_link_args=link_args,
    )
]

setup(
    name="lab10",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages("src"),
    ext_modules=cythonize(ext_modules, compiler_directives={"language_level": "3"}),
)
