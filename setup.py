from setuptools import setup
from statistics_neighborhoods import __version__

setup(
    name='statistics_neighborhoods',
    version=__version__,
    description='Census Information Theory Calculations for Neighborhoods',
    long_description=open('readme.md').read(),
    keywords='census information-theory python',
    author='Joe Hand',
    author_email='joe.a.hand@gmail.com',
    url='https://github.com/SFI-Cities/statistics-neighborhoods',
    license='MIT',
    download_url= 'https://github.com/SFI-Cities/statistics-neighborhoods',
    packages=[],
    install_requires=[
        numpy>=1.9.2,
        pandas>=0.16.2,
        scipy>=0.15.1,
    ],
    entry_points={
        'console_scripts': []
    },

)