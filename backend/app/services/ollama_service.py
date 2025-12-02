"""
Ollama client wrapper for LLM interactions.
"""

import json
import ollama
from typing import Optional, Dict, Any
from loguru import logger


class OllamaClient:
    """Wrapper for Ollama API with error handling and utilities."""
    
    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "gpt-oss:20b"):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama server URL
            default_model: Default model to use for generation
        """
        self.base_url = base_url
        self.default_model = default_model
        self.client = ollama.Client(host=base_url)
        logger.info(f"OllamaClient initialized with base_url={base_url}, model={default_model}")
    
    def generate(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Generate completion from Ollama.
        
        Args:
            prompt: Input prompt
            model: Model name (uses default if None)
            max_tokens: Maximum tokens to generate (limits response length)
            temperature: Sampling temperature (0.0-1.0, lower = more focused)
            
        Returns:
            Generated text
            
        Raises:
            Exception: If generation fails
        """
        model = model or self.default_model
        
        try:
            logger.debug(f"Generating with model={model}, prompt_length={len(prompt)}")
            
            # Build generation options
            options = {
                "temperature": temperature,
            }
            
            if max_tokens:
                options["num_predict"] = max_tokens
            
            response = self.client.generate(
                model=model, 
                prompt=prompt,
                options=options
            )
            result = response['response']
            logger.debug(f"Generated response length: {len(result)}")
            return result
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    def generate_json(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate structured JSON output.
        
        Args:
            prompt: Input prompt requesting JSON output
            model: Model name
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            json.JSONDecodeError: If response is not valid JSON
            Exception: If generation fails
        """
        response_text = self.generate(prompt, model)
        
        # Extract JSON from response (handle markdown code blocks)
        json_text = self._extract_json(response_text)
        
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            raise
    
    def _extract_json(self, text: str) -> str:
        """
        Extract JSON from markdown code blocks if present.
        
        Args:
            text: Response text that may contain JSON
            
        Returns:
            Clean JSON text
        """
        text = text.strip()
        
        # Remove ```json and ``` markers if present
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        
        if text.endswith('```'):
            text = text[:-3]
        
        return text.strip()
    
    def test_connection(self) -> bool:
        """
        Test connection to Ollama server.
        
        Returns:
            True if connection is successful
        """
        try:
            # Try a simple generation
            response = self.generate("Test", model=self.default_model)
            logger.info("Ollama connection test successful")
            return True
        except Exception as e:
            logger.error(f"Ollama connection test failed: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the configured model.
        
        Returns:
            Dictionary with model information
        """
        try:
            # Try to get model info (this is a placeholder - actual implementation may vary)
            return {
                "model": self.default_model,
                "base_url": self.base_url,
                "status": "connected" if self.test_connection() else "disconnected"
            }
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {
                "model": self.default_model,
                "base_url": self.base_url,
                "status": "error",
                "error": str(e)
            }
