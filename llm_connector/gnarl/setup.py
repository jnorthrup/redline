"""
Setup script for the GNARL package.
"""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="redline",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "redline_supervisor_demo=redline.demo_supervisor:interactive_demo",
        ],
    },
    install_requires=[
        "python-dotenv",
        # ...other dependencies...
    ],
    author="Your Name",
    description="GNARL: Generative Neural Adaptive Reasoning Layer",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
