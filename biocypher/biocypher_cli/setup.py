"""
Setup script for BioCypher CLI
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "BioCypher CLI - Advanced DNA Cryptography System"

# Read requirements
req_path = Path(__file__).parent / "requirements.txt"
if req_path.exists():
    with open(req_path, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "click>=8.0.0",
        "rich>=13.0.0", 
        "cryptography>=41.0.0",
        "PyYAML>=6.0",
        "tqdm>=4.65.0"
    ]

setup(
    name="biocypher-cli",
    version="1.0.0",
    author="James Utley",
    author_email="your.email@example.com",
    description="Advanced DNA Cryptography System - Command Line Interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/biocypher-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "biocypher=biocypher_cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "biocypher_cli": ["*.yaml", "*.yml"],
    },
    keywords="dna cryptography bioinformatics nanopore encryption",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/biocypher-cli/issues",
        "Source": "https://github.com/yourusername/biocypher-cli",
        "Documentation": "https://github.com/yourusername/biocypher-cli/wiki",
    },
)