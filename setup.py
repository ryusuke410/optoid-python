from setuptools import setup

setup(
    install_requires=[
        'dependency1',
        'dependency2>=1.0',
        'dependency3<2.0',
    ],
)
