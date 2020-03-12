from distutils.core import setup

from jc import __version__

setup(
    name='jc',
    version=__version__,
    license='MIT',
    description='Simple and straightforward CLI calculator',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Juho Junnila',
    author_email='juho@jnnl.eu',
    url='https://github.com/jnnl/jc',
    packages=['jc',],
    entry_points={
        'console_scripts': ['jc = jc.cli:main',],
    },
    python_requires='>=2.7',
)
