"""
Setup module for the jupyterlab-telemetry
"""
import io
import os.path as osp
from setuptools import setup, find_packages

HERE = osp.dirname(osp.realpath(__file__))

name = "jupyter_telemetry"

path = osp.realpath("{0}/{1}/_version.py".format(HERE, name))
version_ns = {}
with io.open(path, encoding="utf8") as f:
    exec(f.read(), {}, version_ns)

with open(osp.join(HERE, 'README.md')) as fid:
    long_description = fid.read()

setup(
    name=name,
    version=version_ns["__version__"],
    description='Jupyter telemetry library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    author          = 'Jupyter Development Team',
    author_email    = 'jupyter@googlegroups.com',
    url             = 'http://jupyter.org',
    license         = 'BSD',
    platforms       = "Linux, Mac OS X, Windows",
    keywords        = ['Jupyter', 'JupyterLab'],
    python_requires = '>=3.5',
    classifiers     = [
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'jsonschema',
        'python-json-logger',
        'traitlets',
        'ruamel.yaml'
    ],
)
