from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='fogbow-utils',

    version='0.0.1',

    description='',

    url='',

    author='',
    author_email='',

    license='Apache 2.0',

    classifiers=[
        'Development Status :: 1 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: Apache 2.0',

        'Programming Language :: Python :: 3.8',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=['requests'],

    entry_points={
        'console_scripts': [
            'test=main.main:main',
        ],
    },
)
