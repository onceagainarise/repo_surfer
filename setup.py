from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="repo-surfer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A terminal-based AI agent for GitHub repository analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/repo-surfer",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'repo-surfer=repo_surfer.__main__:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.8',
    install_requires=[
        'click>=8.1.7',
        'python-dotenv>=1.0.0',
        'requests>=2.31.0',
        'GitPython>=3.1.40',
        'chromadb>=0.4.22',
        'sentence-transformers>=2.2.2',
        'rich>=13.7.0',
        'PyGithub>=2.1.1',
        'python-magic>=0.4.27',
        'tqdm>=4.66.1',
        'torch>=2.0.0',
        'transformers>=4.30.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'isort>=5.12.0',
            'mypy>=1.0.0',
            'flake8>=6.0.0',
        ],
    },
)
