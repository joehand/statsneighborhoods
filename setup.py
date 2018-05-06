from setuptools import setup
from statsneighborhoods import __version__

setup(
    name='statsneighborhoods',
    version=__version__,
    description='Census Information Theory Calculations for Neighborhoods',
    long_description=open('readme.md').read(),
    keywords='census information-theory python',
    author='Joe Hand',
    author_email='joe.a.hand@gmail.com',
    url='https://github.com/joehand/statsneighborhoods',
    license='MIT',
    download_url= 'https://github.com/joehand/statsneighborhoods',
    packages=[],
#     install_requires=[
#         numpy,
#         pandas,
#         scipy,
#     ],
    entry_points={
        'console_scripts': []
    },

)
