"""
Prompt Manager for Pokemon Crystal AI Agent
Handles loading and managing different prompt types for the AI system.
"""

import os
from enum import Enum
from typing import Optional

class PromptType(Enum):
    """Types of prompts available in the system"""
    SYSTEM = "system_prompt.txt"
    SELF_CRITIC = "self_critic_prompt.txt"
    SUMMARY = "summary_prompt.txt"
    PATHFINDING = "pathfinding_prompt.txt"
    KNOWLEDGE_SEARCH = "knowledge_search_prompt.txt"

class PromptManager:
    """Manages loading and accessing different AI prompts"""

    def __init__(self, prompts_dir: str = "prompts"):
        """
        Initialize the prompt manager.

        Args:
            prompts_dir: Directory containing prompt text files
        """
        self.prompts_dir = prompts_dir
        self._cache = {}

    def load_prompt(self, prompt_type: PromptType) -> str:
        """
        Load a prompt from file, with caching.

        Args:
            prompt_type: Type of prompt to load

        Returns:
            The prompt text

        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        # Check cache first
        if prompt_type in self._cache:
            return self._cache[prompt_type]

        # Load from file
        file_path = os.path.join(self.prompts_dir, prompt_type.value)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            prompt_text = f.read()

        # Cache it
        self._cache[prompt_type] = prompt_text

        return prompt_text

    def get_system_prompt(self) -> str:
        """Get the main system prompt"""
        return self.load_prompt(PromptType.SYSTEM)

    def get_self_critic_prompt(self) -> str:
        """Get the self-criticism analysis prompt"""
        return self.load_prompt(PromptType.SELF_CRITIC)

    def get_summary_prompt(self) -> str:
        """Get the gameplay summary prompt"""
        return self.load_prompt(PromptType.SUMMARY)

    def get_pathfinding_prompt(self) -> str:
        """Get the pathfinding assistant prompt"""
        return self.load_prompt(PromptType.PATHFINDING)

    def get_knowledge_search_prompt(self) -> str:
        """Get the knowledge search prompt"""
        return self.load_prompt(PromptType.KNOWLEDGE_SEARCH)

    def reload_prompts(self):
        """Clear cache and force reload of all prompts"""
        self._cache.clear()

    def build_message_with_context(self,
                                   base_prompt_type: PromptType,
                                   additional_context: Optional[str] = None) -> str:
        """
        Build a complete prompt message with optional additional context.

        Args:
            base_prompt_type: The base prompt to use
            additional_context: Additional context to append

        Returns:
            Complete prompt text
        """
        prompt = self.load_prompt(base_prompt_type)

        if additional_context:
            prompt = f"{prompt}\n\n{additional_context}"

        return prompt
