"""
LLM Manager for handling Groq-hosted model interactions
"""
from pathlib import Path
import mimetypes
import logging
import os
import json
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMManager:
    """Manager for Groq-hosted LLM operations via API"""

    def __init__(self, model_name: str = "deepseek-r1-distill-llama-70b", api_key: str = None):
        """
        Initialize the LLM manager with Groq API

        Args:
            model_name: Name of the Groq-hosted model
            api_key: API key for Groq (from env var if not provided)
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key not set. Pass `api_key` or set `GROQ_API_KEY` env var.")

        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def explain_file(self, file_path: Path) -> str:
        """
        Explain the contents of a file using Groq-hosted LLM.
        """
        try:
            content = self._read_file(file_path)
            if not content:
                return "Unable to read or empty file."
            
            prompt = self._create_explanation_prompt(file_path, content)
            explanation = self.generate_text(prompt, max_length=1000)
            return explanation.strip()
        except Exception as e:
            logger.error(f"Error explaining file {file_path}: {e}")
            return f"Error generating explanation: {str(e)}"

    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Chat with the AI about the repository
        
        Args:
            message: User's message
            context: Optional context to include in the prompt
            
        Returns:
            str: AI's response
        """
        try:
            # Prepare the chat prompt
            prompt = f"""You are a helpful AI assistant for a code repository. 
            The user is asking: {message}
            
            Please provide a helpful response based on your knowledge of software development.
            If the question is about the repository, you can analyze the codebase to provide better answers.
            """
            
            if context:
                prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
                
            return self.generate_text(prompt, max_length=1500).strip()
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"I encountered an error while processing your request: {str(e)}"

    def _read_file(self, file_path: Path):
        """Read and return the content of a file with basic validation."""
        if not file_path.exists() or not file_path.is_file():
            return None
        if file_path.stat().st_size > 1_000_000:  # limit 1MB
            return None
        try:
            return file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    def _create_explanation_prompt(self, file_path: Path, content: str) -> str:
        """Create a prompt for explaining the file content."""
        file_type = mimetypes.guess_type(file_path)[0] or "unknown"
        file_ext = file_path.suffix.lower()
        
        return f"""I need you to explain the following file: {file_path.name}
File type: {file_type} ({file_ext})

The file content is:
{content}

Please provide a detailed explanation of what this file does, including:
1. The purpose of the file
2. Key functions/classes and their roles
3. Important variables and their purposes
4. Any notable patterns or design decisions
5. Dependencies or requirements

Format your response in clear, well-structured markdown.
"""

    def generate_text(self, prompt: str, max_length: int = 500) -> str:
        """
        Generate text using Groq API.
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "You are a helpful coding assistant."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": max_length,
                "temperature": 0.7,
                "top_p": 0.9,
            }

            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return f"Error generating response: {str(e)}"
