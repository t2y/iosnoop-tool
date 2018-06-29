import os
import re
import sys

from setuptools import setup

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

main_py = open('iosnoop/main.py').read()
metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", main_py))

setup(
    name='iosnoop-tool',
    version=metadata['version'],
    description='parse and visualize iosnoop output',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries',
    ],
    keywords=['iosnoop'],
    author='Tetsuya Morimoto',
    author_email='tetsuya.morimoto@gmail.com',
    url='https://github.com/t2y/iosnoop-tool',
    license='Apache License 2.0',
    platforms=['unix', 'linux', 'osx', 'windows'],
    packages=['iosnoop'],
    include_package_data=True,
    install_requires=['numpy', 'matplotlib', 'seaborn', 'pandas'],
    tests_require=['tox', 'pytest', 'pytest-pep8', 'pytest-flakes'],
    entry_points = {
        'console_scripts': [
            'iosnoop-cli=iosnoop.main:main',
        ],
    },
)
