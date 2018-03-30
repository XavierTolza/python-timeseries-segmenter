from setuptools import setup

setup(
    name='dataframesegmenter',
    version='1.0',
    description="Interactively clusterize your timeseries datasets",
    packages=["dataframesegmenter"],
    install_requires=[
        "Bcolors >= 0.1",
        "matplotlib>=2.1.2",
        "numpy>=1.14.2"
    ],
    dependency_links=[
        "git+https://github.com/XavierTolza/Bcolors.git@master"
    ]
)
