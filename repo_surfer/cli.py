"""
Command-line interface for RepoSurfer
"""
import click
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from .memory_manager import MemoryManager
import subprocess

@click.group(invoke_without_command=True)
@click.option('--debug/--no-debug', default=False, help='Enable debug mode')
@click.pass_context
def cli(ctx: click.Context, debug: bool):
    """RepoSurfer - AI-powered GitHub repository analyzer"""
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    
    if ctx.invoked_subcommand is None:
        click.echo("Welcome to RepoSurfer! Use --help to see available commands.")

@cli.command()
@click.argument('repo_path')
@click.pass_context
def analyze(ctx: click.Context, repo_path: str):
    """
    Analyze a GitHub repository or local directory.
    
    Examples:
        repo-surfer analyze .                     # Analyze current directory
        repo-surfer analyze /path/to/repo        # Analyze local repository
        repo-surfer analyze user/repo            # Analyze GitHub repository
        repo-surfer analyze https://github.com/user/repo
    """
    from pathlib import Path
    import subprocess
    from urllib.parse import urlparse
    import os
    import json
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress
    
    console = Console()
    
    try:
        # Check if it's a local path
        if os.path.exists(repo_path):
            repo_dir = Path(repo_path).resolve()
            if not (repo_dir / '.git').exists():
                click.echo(f"Error: {repo_path} is not a Git repository", err=True)
                return
        else:
            # It's a GitHub URL or username/repo format
            if not (repo_path.startswith('http') or '/' in repo_path):
                click.echo("Error: Invalid repository path or URL", err=True)
                return
                
            # Clone the repository to a temporary directory
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix='repo-surfer-')
            repo_dir = Path(temp_dir) / repo_path.split('/')[-1]
            
            if not repo_path.startswith('http'):
                repo_path = f"https://github.com/{repo_path}.git"
            
            with console.status(f"[bold green]Cloning repository {repo_path}...") as status:
                result = subprocess.run(
                    ['git', 'clone', '--depth', '1', repo_path, str(repo_dir)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    console.print(f"[red]Error cloning repository: {result.stderr}")
                    return
        
        # Analyze the repository
        with console.status("[bold green]Analyzing repository...") as status:
            # Get repository info
            result = subprocess.run(
                ['git', 'remote', '-v'],
                cwd=repo_dir,
                capture_output=True,
                text=True
            )
            remote_url = result.stdout.split('\n')[0].split('\t')[1].split(' ')[0] if result.returncode == 0 else "Unknown"
            
            # Get commit count
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                cwd=repo_dir,
                capture_output=True,
                text=True
            )
            commit_count = result.stdout.strip() if result.returncode == 0 else "Unknown"
            
            # Get file count and sizes
            result = subprocess.run(
                ['git', 'ls-files'],
                cwd=repo_dir,
                capture_output=True,
                text=True
            )
            files = result.stdout.splitlines() if result.returncode == 0 else []
            file_count = len(files)
            
            # Get language stats
            result = subprocess.run(
                ['git', 'ls-files', '|', 'xargs', 'wc', '-l'],
                cwd=repo_dir,
                shell=True,
                capture_output=True,
                text=True
            )
            total_lines = result.stdout.split('\n')[-2].strip().split()[0] if result.returncode == 0 and result.stdout.strip() else "Unknown"
            
            # Get recent commits
            result = subprocess.run(
                ['git', 'log', '--pretty=format:%h - %s (%cr) <%an>', '-n', '5'],
                cwd=repo_dir,
                capture_output=True,
                text=True
            )
            recent_commits = result.stdout.split('\n') if result.returncode == 0 else []
        
        # Display results
        console.print("\n[bold blue]Repository Analysis[/bold blue]")
        console.print(f"[bold]Location:[/bold] {repo_dir}")
        console.print(f"[bold]Remote:[/bold] {remote_url}")
        console.print(f"[bold]Commits:[/bold] {commit_count}")
        console.print(f"[bold]Files:[/bold] {file_count}")
        console.print(f"[bold]Lines of code:[/bold] {total_lines}")
        
        if recent_commits:
            console.print("\n[bold]Recent Commits:[/bold]")
            for commit in recent_commits:
                console.print(f"• {commit}")
                
        console.print("\n[bold green]Analysis complete![/bold green]")
        console.print("\nNext steps:")
        console.print("1. Use 'repo-surfer structure .' to explore the repository structure")
        console.print("2. Use 'repo-surfer explain <file>' to understand specific files")
        
    except Exception as e:
        console.print(f"[red]Error during analysis: {str(e)}[/red]")
        if ctx.obj.get('DEBUG'):
            import traceback
            console.print(traceback.format_exc())

@cli.command()
@click.argument('repo_url')
@click.option('--output-dir', '-o', type=click.Path(), default='.', help='Output directory for cloned repository')
@click.pass_context
def clone(ctx: click.Context, repo_url: str, output_dir: str):
    """
    Clone a GitHub repository.
    
    Example:
        repo-surfer clone https://github.com/username/repo.git
        repo-surfer clone git@github.com:username/repo.git --output-dir ./my-repo
    """
    import os
    import subprocess
    from pathlib import Path
    from urllib.parse import urlparse
    
    try:
        output_path = Path(output_dir).resolve()
        
        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Check if the directory is empty
        if any(output_path.iterdir()):
            click.confirm(
                f"Directory '{output_dir}' is not empty. Continue anyway?",
                abort=True
            )
        
        click.echo(f"Cloning repository: {repo_url} to {output_path}")
        
        # Run git clone
        result = subprocess.run(
            ['git', 'clone', repo_url, str(output_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            click.echo(f"Successfully cloned repository to {output_path}")
            
            # Get repository name from URL
            repo_name = Path(urlparse(repo_url).path).stem
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
                
            click.echo(f"\nNext steps:")
            click.echo(f"1. cd {output_path / repo_name if repo_name else output_path}")
            click.echo("2. repo-surfer analyze .")
        else:
            click.echo(f"Error cloning repository: {result.stderr}", err=True)
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        if ctx.obj.get('DEBUG'):
            import traceback
            click.echo(traceback.format_exc())

@cli.command()
@click.argument('repo_path', type=click.Path(exists=True))
@click.option('--depth', '-d', type=int, default=3, help='Maximum depth to display')
@click.option('--show-hidden/--no-hidden', default=False, help='Show hidden files and directories')
@click.pass_context
def structure(ctx: click.Context, repo_path: str, depth: int, show_hidden: bool):
    """
    Show repository structure with file statistics.
    
    Examples:
        repo-surfer structure .                     # Show current directory structure
        repo-surfer structure /path/to/repo        # Show specific repository structure
        repo-surfer structure . --depth 2          # Limit depth to 2 levels
        repo-surfer structure . --show-hidden      # Include hidden files/directories
    """
    from rich.console import Console
    from rich.tree import Tree
    from rich.text import Text
    import os
    from pathlib import Path
    
    console = Console()
    repo_path = Path(repo_path).resolve()
    
    def get_size(path: Path) -> str:
        """Get human-readable size of a file or directory"""
        if path.is_file():
            size = path.stat().st_size
        else:
            size = sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())
            
        # Convert to human-readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def should_skip(path: Path) -> bool:
        """Determine if a path should be skipped"""
        # Skip hidden files/directories unless explicitly requested
        if not show_hidden and path.name.startswith('.'):
            return True
        # Skip common directories that aren't typically useful to show
        skip_dirs = {'__pycache__', '.git', '.github', '.idea', 'venv', 'env', 'node_modules'}
        if path.name in skip_dirs:
            return True
        return False
    
    def build_tree(path: Path, tree: Tree, current_depth: int = 0):
        """Recursively build the directory tree"""
        if should_skip(path):
            return
            
        if path.is_file():
            size = get_size(path)
            tree.add(f"{path.name} [dim]({size})[/]")
            return
            
        # For directories, add a node and recurse
        if current_depth >= depth:
            return
            
        dir_node = tree.add(f"[bold]{path.name}/[/]")
        try:
            # Sort directories first, then files, both alphabetically
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            for item in items:
                build_tree(item, dir_node, current_depth + 1)
        except (PermissionError, OSError) as e:
            dir_node.add(f"[red]Error reading: {e}[/]")
    
    try:
        console.print(f"[bold blue]Repository Structure:[/] [dim]{repo_path}[/]\n")
        
        # Show repository info if it's a git repo
        if (repo_path / '.git').exists():
            result = subprocess.run(
                ['git', 'remote', '-v'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                remote = result.stdout.split('\n')[0].split('\t')[1].split(' ')[0]
                console.print(f"[bold]Remote:[/] {remote}")
        
        # Build and display the tree
        tree = Tree(f"[bold]{repo_path.name}/[/]")
        build_tree(repo_path, tree)
        console.print(tree)
        
        # Show summary
        file_count = sum(1 for _ in repo_path.glob('**/*') if _.is_file() and not should_skip(_))
        dir_count = sum(1 for _ in repo_path.glob('**/') if not should_skip(_)) - 1  # -1 to exclude self
        total_size = get_size(repo_path)
        
        console.print("\n[bold]Summary:[/]")
        console.print(f"• Files: {file_count:,}")
        console.print(f"• Directories: {dir_count:,}")
        console.print(f"• Total size: {total_size}")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/]")
        if ctx.obj.get('DEBUG'):
            import traceback
            console.print(traceback.format_exc())

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.pass_context
def explain(ctx: click.Context, file_path: str):
    """Explain a file's contents"""
    from rich.console import Console
    from rich.markdown import Markdown
    from .llm_manager import LLMManager
    
    console = Console()
    file_path = Path(file_path).resolve()
    
    with console.status(f"[bold green]Analyzing {file_path.name}...") as status:
        # Initialize LLM manager
        llm = LLMManager()
        
        # Get explanation
        explanation = llm.explain_file(file_path)
        
        # Print the explanation with nice formatting
        console.print(f"\n[bold]Explanation for {file_path.name}:[/bold]\n")
        console.print(Markdown(explanation))
@cli.group()
@click.pass_context
def memory(ctx: click.Context):
    """Manage conversation memory"""
    from .memory_manager import MemoryManager
    ctx.obj['memory_manager'] = MemoryManager()

@memory.command('search')
@click.argument('query')
@click.option('--limit', '-l', type=int, default=5, help='Maximum number of results to return')
@click.pass_context
def search_memory(ctx: click.Context, query: str, limit: int):
    """Search conversation memory"""
    memory_manager = ctx.obj['memory_manager']
    results = memory_manager.search_memory(query, n_results=limit)
    
    if not results:
        click.echo("No matching memories found.")
        return
        
    click.echo(f"Found {len(results)} matching memories:")
    for i, result in enumerate(results, 1):
        click.echo(f"\n--- Result {i} ---")
        click.echo(f"Query: {result['metadata'].get('query', 'N/A')}")
        click.echo(f"Response: {result['document']}")
        if 'timestamp' in result['metadata']:
            click.echo(f"Timestamp: {result['metadata']['timestamp']}")

@memory.command('clear')
@click.pass_context
def clear_memory(ctx: click.Context):
    """Clear conversation memory"""
    if click.confirm('Are you sure you want to clear all conversation memory? This cannot be undone.', abort=False):
        memory_manager = ctx.obj['memory_manager']
        # ChromaDB doesn't have a direct clear method, so we'll recreate the collection
        memory_manager.client.delete_collection("conversation_memory")
        memory_manager.collection = memory_manager.client.get_or_create_collection("conversation_memory")
        click.echo("Successfully cleared conversation memory.")

@cli.command()
@click.argument('message')
@click.pass_context
def chat(ctx: click.Context, message: str):
    """Chat with the AI about the repository"""
    from rich.console import Console
    from rich.markdown import Markdown
    from .llm_manager import LLMManager
    
    console = Console()
    llm = LLMManager()
    memory_manager = MemoryManager()
    
    # Get response from LLM
    with console.status("[bold green]Thinking...") as status:
        response = llm.chat(message)
        
        # Store conversation in memory
        memory_manager.add_conversation(
            query=message,
            response=response,
            metadata={"timestamp": datetime.now().isoformat()}
        )
        
        # Print the response
        console.print("\n[bold]AI:[/bold]")
        console.print(Markdown(response))

def main():
    cli(obj={})

if __name__ == '__main__':
    main()
