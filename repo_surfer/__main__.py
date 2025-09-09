"""
Main entry point for RepoSurfer
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from .cli import cli

def main():
    """Main entry point"""

    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    
    # Run 
    cli()

if __name__ == "__main__":
    main()
