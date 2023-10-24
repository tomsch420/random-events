import codecs
import os

from setuptools import setup

long_description = """Probabilistic Machine Learning frequently requires descriptions of random variables and events
that are shared among many packages.This package provides a common interface for describing random variables and events,
 providing usable and easily extensible classes."""


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(name='random_events',
      version=get_version(os.path.join("src", "random_events", "__init__.py")),
      description='Define random events for probabilistic reasoning',
      long_description=long_description,
      long_description_content_type='text/plain',
      author='Tom Schierenbeck',
      author_email='tom_sch@uni-bremen.de',
      url='https://github.com/tomsch420/random-events',
      packages=['random_events'],
      install_requires=["setuptools", "portion", "pydantic"],
      keywords='random events probabilistic machine learning probability theory variables',
      project_urls={'Source': 'https://github.com/tomsch420/random-events',
                    'Documentation': 'TODO'},
      python_requires='>=3.6',
      package_dir={'': 'src'}, )
