"""
Setup module for the jupyterlab-telemetry
"""
from setuptools import setup, find_packages

setup(
    name='jupyter_telemetry',
    version='0.0.5',
    description='Jupyter telemetry library',
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
