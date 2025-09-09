"""
RepoSurfer - A powerful terminal-based AI agent for GitHub repository analysis and exploration.

This package provides tools to analyze and explore GitHub repositories directly from the terminal,
with features like code search, structure visualization, and AI-powered insights.
"""

__version__ = "0.1.0"
__author__ = "Your Name <your.email@example.com>"
__license__ = "MIT"

# Import main components to make them available at the package level
from .cli import cli
from .github_handler import GitHubHandler
from .llm_manager import LLMManager
from .memory_manager import MemoryManager

__all__ = ["cli", "GitHubHandler", "LLMManager", "MemoryManager"]
