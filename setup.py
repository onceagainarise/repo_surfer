import os
from setuptools import setup, find_packages

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
def get_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="repo-surfer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A terminal-based AI agent for GitHub repository analysis and exploration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/repo-surfer",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={
        "repo_surfer": ["py.typed"],
    },
    entry_points={
        'console_scripts': [
            'repo-surfer=repo_surfer.__main__:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    python_requires='>=3.8',
    install_requires=get_requirements(),
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'isort>=5.12.0',
            'mypy>=1.0.0',
            'types-requests>=2.31.0',
            'types-python-dotenv>=1.0.0',
            'twine>=4.0.0',
            'build>=0.10.0',
            'flake8>=6.0.0',
        ],
    },
)
