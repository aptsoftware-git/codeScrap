"""
Ollama client wrapper for LLM interactions.
"""

import json
import asyncio
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
            logger.info(f"LLM call: model={model}, max_tokens={max_tokens}, temp={temperature}, prompt_len={len(prompt)}")
            
            # Build generation options optimized for 16GB RAM, 4-core CPU
            options = {
                "temperature": temperature,
                "num_ctx": 1024,  # Reduced context window (was 1536) to save memory
                "num_thread": 4,  # Match CPU cores (was 10) - 4 cores = 8 threads
                "num_gpu": 0,     # CPU only
                "top_k": 20,      # Reasonable diversity
                "top_p": 0.9,     # Good nucleus sampling
                "repeat_penalty": 1.1,  # Reduce repetition
                "num_batch": 128, # Smaller batch size to reduce memory usage
            }
            
            if max_tokens:
                options["num_predict"] = max_tokens
            
            response = self.client.generate(
                model=model, 
                prompt=prompt,
                options=options
            )
            result = response['response']
            logger.info(f"LLM response: {len(result)} chars generated")
            return result
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    async def generate_async(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Async version of generate that runs in thread pool to avoid blocking.
        
        Args:
            prompt: Input prompt
            model: Model name (uses default if None)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        # Run the blocking generate call in a thread pool
        return await asyncio.to_thread(
            self.generate,
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
    
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


# Global instance (initialized in main.py on startup, or on-demand)
ollama_client: Optional[OllamaClient] = None

