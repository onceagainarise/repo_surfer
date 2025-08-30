# Repo Surfer 🏄‍♂️

A powerful terminal-based AI agent for GitHub repository analysis and exploration. Dive deep into any repository, understand its structure, and get intelligent insights without leaving your terminal.


[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- **Repository Analysis**: Get detailed insights into any GitHub repository
- **Interactive Chat**: Ask questions about the repository's codebase
- **Structure Visualization**: View repository structure with file sizes and types
- **Commit History**: Browse through commit history and changes
- **Local & Remote Support**: Analyze both local and remote repositories
- **Memory Management**: Persistent conversation history using ChromaDB

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/repo-surfer.git
   cd repo-surfer
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## 🛠️ CLI Commands

### `analyze` - Analyze a Repository
Analyze a GitHub repository or local directory to get insights and statistics.

```bash
# Analyze current directory
repo-surfer analyze .

# Analyze local repository
repo-surfer analyze /path/to/repo

# Analyze GitHub repository (username/repo format)
repo-surfer analyze username/repo

# Analyze GitHub repository using URL
repo-surfer analyze https://github.com/username/repo
```

### `clone` - Clone a Repository
Clone a GitHub repository to a local directory.

```bash
# Basic clone
repo-surfer clone https://github.com/username/repo.git

# Clone to specific directory
repo-surfer clone git@github.com:username/repo.git --output-dir ./my-repo
```

### `structure` - View Repository Structure
Display the repository structure with file sizes and statistics.

```bash
# Show current directory structure (default depth: 3)
repo-surfer structure .

# Show specific repository structure
repo-surfer structure /path/to/repo

# Limit directory depth
repo-surfer structure . --depth 2

# Include hidden files and directories
repo-surfer structure . --show-hidden
```

### `explain` - Explain File Contents
Get an AI-generated explanation of a file's contents.

```bash
# Explain a file
repo-surfer explain path/to/file.py
```

### `chat` - Interactive AI Chat
Chat with the AI about the repository.

```bash
# Start a chat session
repo-surfer chat "Your question about the codebase"
```

### Memory Management
Manage conversation memory and search through past interactions.

```bash
# Search conversation history
repo-surfer memory search "search query" --limit 5

# Clear all conversation history
repo-surfer memory clear
```

## ⚙️ Configuration

Create a `.env` file in the project root with the following variables:

```env
# Optional: Set your GitHub token for higher rate limits
GITHUB_TOKEN=your_github_token_here

# Debug mode (true/false)
DEBUG=false
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ and Python
- Uses [ChromaDB](https://www.trychroma.com/) for vector storage
- Inspired by the need for better repository exploration tools

---

<p align="center">
  Made with ✨ by Your Name | 🌍 <a href="https://yourwebsite.com">yourwebsite.com</a>
</p>
