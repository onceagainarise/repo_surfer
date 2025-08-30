"""
GitHub repository interaction module
"""
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import requests
from github import Github, GithubException
from github.Repository import Repository
import git

class GitHubHandler:
    """Handle GitHub repository operations"""
    
    def __init__(self, github_token: Optional[str] = None):
        """Initialize GitHub handler with optional API token"""
        self.github = Github(github_token) if github_token else Github()
        self.rate_limit = self.github.get_rate_limit()
    
    def get_repo_info(self, repo_url: str) -> Dict[str, Any]:
        """Get repository information from GitHub API"""
        try:
            # Extract owner and repo name from URL
            if 'github.com' in repo_url:
                parts = repo_url.rstrip('/').split('/')
                repo_name = f"{parts[-2]}/{parts[-1]}"
            else:
                repo_name = repo_url
                
            repo = self.github.get_repo(repo_name)
            
            return {
                'name': repo.name,
                'full_name': repo.full_name,
                'description': repo.description,
                'url': repo.html_url,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'watchers': repo.watchers_count,
                'language': repo.language,
                'license': repo.license.key if repo.license else None,
                'created_at': repo.created_at.isoformat(),
                'updated_at': repo.updated_at.isoformat(),
                'topics': repo.get_topics(),
                'open_issues': repo.open_issues_count,
                'default_branch': repo.default_branch,
                'subscribers_count': repo.subscribers_count,
                'network_count': repo.network_count,
                'has_issues': repo.has_issues,
                'has_projects': repo.has_projects,
                'has_wiki': repo.has_wiki,
                'has_downloads': repo.has_downloads,
                'archived': repo.archived,
                'disabled': repo.disabled,
                'visibility': repo.visibility,
                'size': repo.size,  # in KB
            }
            
        except GithubException as e:
            return {
                'error': str(e),
                'message': 'Failed to fetch repository information'
            }
    
    def clone_repository(self, repo_url: str, target_dir: str) -> Dict[str, Any]:
        """Clone a GitHub repository to the specified directory"""
        try:
            # Ensure target directory exists
            target_path = Path(target_dir).expanduser().resolve()
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Clone the repository
            repo = git.Repo.clone_from(repo_url, target_path)
            
            return {
                'success': True,
                'path': str(target_path),
                'branch': repo.active_branch.name,
                'commit': repo.head.commit.hexsha,
                'message': 'Repository cloned successfully'
            }
            
        except git.GitCommandError as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to clone repository'
            }
    
    def get_repo_structure(self, repo_path: str) -> Dict[str, Any]:
        """Get the file and directory structure of a local repository"""
        try:
            repo_path = Path(repo_path).resolve()
            
            if not (repo_path / '.git').exists():
                return {
                    'error': 'Not a git repository',
                    'message': 'The specified path is not a git repository'
                }
            
            def get_tree(path: Path, level: int = 0) -> List[Dict]:
                """Recursively build directory tree"""
                result = []
                for item in path.iterdir():
                    if item.name.startswith('.'):
                        continue
                        
                    item_info = {
                        'name': item.name,
                        'type': 'directory' if item.is_dir() else 'file',
                        'path': str(item.relative_to(repo_path)),
                        'size': item.stat().st_size if item.is_file() else 0,
                        'children': get_tree(item, level + 1) if item.is_dir() else []
                    }
                    result.append(item_info)
                return result
            
            return {
                'success': True,
                'name': repo_path.name,
                'path': str(repo_path),
                'structure': get_tree(repo_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to analyze repository structure'
            }
    
    def get_rate_limit(self) -> Dict[str, Any]:
        """Get GitHub API rate limit information"""
        return {
            'limit': self.rate_limit.core.limit,
            'remaining': self.rate_limit.core.remaining,
            'reset': self.rate_limit.core.reset.isoformat()
        }
