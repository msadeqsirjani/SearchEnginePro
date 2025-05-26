#!/usr/bin/env python3
"""
Setup script for SearchEngine Pro
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="searchengine-pro",
    version="3.2.0",
    author="SearchEngine Pro Team",
    author_email="dev@searchengine-pro.com",
    description="A comprehensive interactive console-based web search engine",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/searchengine-pro/searchengine-pro",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "coverage>=7.3.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "apis": [
            "google-api-python-client>=2.100.0",
            "duckduckgo-search>=3.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "searchengine=searchengine.main:main",
            "sepro=searchengine.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "searchengine": [
            "config/*.yaml",
            "config/*.json",
            "data/*.json",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/searchengine-pro/searchengine-pro/issues",
        "Source": "https://github.com/searchengine-pro/searchengine-pro",
        "Documentation": "https://searchengine-pro.readthedocs.io/",
    },
) 