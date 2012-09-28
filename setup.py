#!/usr/bin/env python3.2

from setuptools import setup, find_packages

setup(name='ariblib',
      version='0.0.2',
      author='Chisa Youzaka',
      author_email='ariblib@txqz.net',
      url='http://github.com/youzaka/ariblib',
      classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'Natural Language :: Japanese'
      ],
      license='MIT',
      short_description='python implementation of arib-std-b10 and arib-std-b24',
      packages=find_packages(),
)

