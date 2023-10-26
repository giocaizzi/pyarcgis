from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pyarcgis",
    version="0.0.1",
    description="python 2.7 easy api for ArcMap",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/giocaizzi/pyarcgis",
    author="giocaizzi",
    author_email="giocaizzi@gmail.com",
    license="MIT",
    packages=find_packages(include=["pyarcgis", "pyarcgis/*"]),
    setup_requires=[],
    tests_require=[],
    install_requires=[
    ],
    extras_require={
        "docs": [],
        "dev": [],
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
    ],
    project_urls={
        # "Documentation": "https://giocaizzi.github.io/pysurfline/",
        "Bug Reports": "https://github.com/giocaizzi/pyarcgis/issues",
        "Source": "https://github.com/giocaizzi/pyarcgis",
    },
)
