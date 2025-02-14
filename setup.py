from setuptools import setup, find_packages, Extension
import os
import subprocess
import sys

current_directory = os.path.dirname(os.path.abspath(__file__))

# Ensure pybind11 is installed before importing it


from pybind11.setup_helpers import Pybind11Extension

# Optional project description in README.md:
try:
    with open(os.path.join(current_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except Exception:
    long_description = ''

# Define the extension module for random-events-lib
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

# Function to read the version from random_events.__version__
def get_version():
    version_file = os.path.join(current_directory, 'src', 'random_events', '__init__.py')
    with open(version_file, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")

setup(
    # Project name:
    name='random_events',
    # Packages to include in the distribution:
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    # Project version number:
    version=get_version(),
    # List a license for the project, eg. MIT License
    license='MIT License',
    # Short description of your library:
    description='Random random events for probabilistic reasoning',
    # Long description of your library:
    long_description=long_description,
    long_description_content_type='text/markdown',
    # Your name:
    author='Tom Schierenbeck',
    # Your email address:
    author_email='tom_sch@uni-bremen.de',
    # Link to your github repository or website:
    url='https://github.com/tomsch420/random-events',
    # Download Link from where the project can be downloaded from:
    download_url='https://github.com/tomsch420/random-events',
    # List of keywords:
    keywords=[
        'random events', 'probabilistic machine learning', 'probability theory',
        'variables', 'reasoning under uncertainty'
    ],
    # List project dependencies:
    install_requires=[
        'setuptools', 'setuptools-scm', 'pybind11'
    ],
    # Define the extension modules to be built
    ext_modules=ext_modules,
    # https://pypi.org/classifiers/
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)