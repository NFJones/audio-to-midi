#!/usr/bin/env python3

from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

requirements = []
with open(path.join(here, "requirements.txt"), "r") as infile:
    requirements = [line for line in infile.read().split("\n") if line]

setup(
    name="audio_to_midi",
    version="2019.2",
    description="Convert audio to multichannel MIDI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NFJones/audio-to-midi",
    author="Neil F Jones",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="audio midi conversion",
    packages=["audio_to_midi"],
    python_requires=">=3.5.*, <4",
    entry_points={"console_scripts": ["audio-to-midi = audio_to_midi.main:main"]},
    install_requires=requirements,
)
