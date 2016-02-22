from setuptools import setup, find_packages
from ariblib import __version__


setup(
    name='ariblib',
    version=__version__,
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
    description='python implementation of arib-std-b10 and arib-std-b24',
    packages=find_packages(),
)
