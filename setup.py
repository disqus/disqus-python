#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='disqus-python',
    version='0.4.2',
    author='DISQUS',
    author_email='david@disqus.com',
    url='https://github.com/disqus/disqus-python',
    description = 'Disqus API Bindings',
    packages=find_packages(),
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=[],
    setup_requires=[],
    tests_require=[
        'nose>=1.0',
        'unittest2',
        'mock',
    ],
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
)
