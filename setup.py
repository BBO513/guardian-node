#!/usr/bin/env python3
"""
Guardian Node - Family Cybersecurity Assistant
Setup script for packaging and distribution
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "guardian_interpreter" / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="guardian-node",
    version="1.0.0",
    author="BBO513",
    author_email="support@guardian-node.org",
    description="Privacy-first AI cybersecurity assistant for families",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BBO513/guardian-node",
    project_urls={
        "Bug Tracker": "https://github.com/BBO513/guardian-node/issues",
        "Documentation": "https://github.com/BBO513/guardian-node/tree/main/docs",
        "Source Code": "https://github.com/BBO513/guardian-node",
    },
    packages=find_packages(include=["guardian_interpreter", "guardian_interpreter.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Education",
        "Topic :: Security",
        "Topic :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Environment :: Web Environment",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "voice": [
            "pyttsx3>=2.90",
            "SpeechRecognition>=3.10.0",
            "pocketsphinx>=5.0.0",
        ],
        "network": [
            "python-nmap>=0.7.1",
            "scapy>=2.5.0",
            "netifaces>=0.11.0",
        ],
        "gui": [
            "PySide6>=6.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "guardian-node=guardian_interpreter.main:main",
            "guardian-cli=guardian_interpreter.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "guardian_interpreter": [
            "config.yaml",
            "*.md",
        ],
    },
    zip_safe=False,
    keywords=[
        "cybersecurity",
        "ai",
        "family",
        "privacy",
        "offline",
        "llm",
        "parental-controls",
        "education",
        "security",
        "raspberry-pi",
    ],
    license="MIT",
)
