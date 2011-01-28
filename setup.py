#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='disqus-python',
    version='0.1.0',
    author='DISQUS',
    author_email='david@disqus.com',
    url='http://github.com/disqus/disqus-python',
    description = 'Disqus API Bindings',
    packages=find_packages(),
    zip_safe=False,
    install_requires=['simplejson'],
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)