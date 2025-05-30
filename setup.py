from pybind11.setup_helpers import Pybind11Extension
from setuptools import setup

ext_modules = [
    Pybind11Extension(
        "random_events_lib",  # Python module name
        ["src/random-events-lib/export/bindings.cpp",
         "src/random-events-lib/random_events_lib/src/sigma_algebra.cpp",
         "src/random-events-lib/random_events_lib/src/set.cpp",
         "src/random-events-lib/random_events_lib/src/product_algebra.cpp"],  # C++ binding source
        include_dirs=["src/random-events-lib/random_events_lib/include"],  # Include directory for C++ headers
        extra_compile_args=["-std=c++17", "-fPIC"],
    ),
]

setup(
    ext_modules=ext_modules,
)