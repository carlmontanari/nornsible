#!/usr/bin/env python
"""nornir tag and host/group limit wrapper"""
import setuptools

__author__ = "Carl Montanari"

with open("README.md", "r") as f:
    README = f.read()

setuptools.setup(
    name="nornsible",
    version="2019.10.28",
    author=__author__,
    author_email="carl.r.montanari@gmail.com",
    description="Wrapper for tags and host/group limiting for nornir scripts.",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=["colorama>=0.3.9", "nornir>=2.2.0"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.6",
)
