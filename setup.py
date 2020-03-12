from distutils.core import setup

setup(
    name='jc',
    version='1.0',
    author='Juho Junnila',
    author_email='juho@jnnl.eu',
    url='https://github.com/jnnl/jc',
    entry_points={
        'console_scripts': ['jc = jc.cli:main',],
    },
    packages=['jc',],
    license='MIT',
    long_description=open('README.md').read(),
)
