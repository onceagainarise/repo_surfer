"""
LLM Manager for handling Groq-hosted model interactions
"""
from pathlib import Path
import mimetypes
import logging
import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMManager:
    """Manager for Groq-hosted LLM operations via API"""

    def __init__(self, memory_manager=None, model_name: str = "deepseek-r1-distill-llama-70b", api_key: str = None):
        """
        Initialize the LLM manager with Groq API and memory

        Args:
            memory_manager: Optional MemoryManager instance for conversation history
            model_name: Name of the Groq-hosted model
            api_key: API key for Groq (from env var if not provided)
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key not set. Pass `api_key` or set `GROQ_API_KEY` env var.")

        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Use provided memory manager or create a new one
        if memory_manager is None:
            from .memory_manager import MemoryManager
            self.memory = MemoryManager()
        else:
            self.memory = memory_manager
    
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
        Chat with the AI about the repository with conversation memory
        
        Args:
            message: User's message
            context: Optional context to include in the prompt
            
        Returns:
            str: AI's response
        """
        try:
            # Get recent conversation history
            conversation_history = self.memory.get_conversation_history(limit=5)
            
            # Prepare the system message with clear instructions about context
            system_message = (
                "You are a helpful AI assistant for a code repository. "
                "You are having a conversation with the user. Below is the conversation history, "
                "followed by the user's latest message. Please respond appropriately, "
                "maintaining context from the entire conversation. "
                "If the user refers to previous messages or context, be sure to acknowledge and address those references.\n\n"
            )
            
            # Prepare messages list for the chat completion
            messages = [{"role": "system", "content": system_message}]
            
            # Add conversation history if available
            if conversation_history:
                # Add a summary of the conversation so far
                conversation_summary = "\n".join(
                    f"User: {conv['query']}\nAssistant: {conv['response']}"
                    for conv in conversation_history
                )
                messages.append({
                    "role": "system",
                    "content": f"Conversation history so far:\n{conversation_summary}"
                })
            
            # Add current message with any context
            user_message = message
            if context:
                context_str = "\nContext: " + json.dumps(context, indent=2)
                user_message += context_str
            
            messages.append({"role": "user", "content": user_message})
            
            # Generate response using the chat completion API
            response = self._chat_completion(messages, max_tokens=1500).strip()
            
            # Store the conversation in memory
            self.memory.add_conversation(
                query=message,
                response=response,
                metadata={
                    'model': self.model_name,
                    'context': context or {},
                    'timestamp': int(datetime.now().timestamp())
                }
            )
            
            # Ensure the memory is persisted
            self.memory.save()
            
            return response
            
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

    def generate_text(self, prompt: str, max_length: int = 1000, temperature: float = 0.7) -> str:
        """
        Generate text using the Groq-hosted LLM
        
        Args:
            prompt: The prompt to generate text from
            max_length: Maximum length of the generated text
            temperature: Controls randomness (0.0 to 1.0)
            
        Returns:
            str: Generated text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Split prompt into system message and user message if it contains "Assistant:"
        messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
        
        # Check if prompt contains conversation history
        if "\nUser:" in prompt or "\nAssistant:" in prompt:
            # Parse conversation history from prompt
            lines = prompt.split('\n')
            current_role = None
            current_content = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('User:'):
                    if current_role and current_content:
                        messages.append({"role": current_role, "content": '\n'.join(current_content)})
                    current_role = "user"
                    current_content = [line[5:].strip()]  # Remove "User:" prefix
                elif line.startswith('Assistant:'):
                    if current_role and current_content:
                        messages.append({"role": current_role, "content": '\n'.join(current_content)})
                    current_role = "assistant"
                    current_content = [line[10:].strip()]  # Remove "Assistant:" prefix
                elif current_content is not None:
                    current_content.append(line)
            
            # Add the last message
            if current_role and current_content:
                messages.append({"role": current_role, "content": '\n'.join(current_content)})
        else:
            # Single user message
            messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_length,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return f"Error: {str(e)}"

    def _chat_completion(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> str:
        """
        Generate chat completion using the Groq API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            str: Generated response
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare the data with improved parameters
        data = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "frequency_penalty": 0.2,
            "presence_penalty": 0.2,
            "stop": None
        }
        
        try:
            logger.debug(f"Sending request to Groq API with data: {json.dumps(data, indent=2)}")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            response_json = response.json()
            
            # Log the response for debugging
            logger.debug(f"Received response from Groq API: {json.dumps(response_json, indent=2)}")
            
            return response_json["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error in chat completion: {str(e)}")
            return "I'm having trouble connecting to the AI service. Please try again in a moment."
            
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing response from Groq API: {str(e)}")
            return "I received an unexpected response from the AI service. Please try again."
            
        except Exception as e:
            logger.error(f"Unexpected error in chat completion: {str(e)}")
            return "I encountered an unexpected error while generating a response. Please try again later."
