"""
LLM Router: Intelligent routing between Ollama and Claude.
Handles provider selection, fallback logic, and unified interface.
"""

from typing import Optional, Dict, Any, Tuple
from loguru import logger

from app.services.ollama_service import OllamaClient
from app.services.claude_service import claude_service
from app.settings import settings


class LLMRouter:
    """
    Route LLM requests to appropriate provider with fallback support.
    
    Features:
    - Provider selection (ollama/claude)
    - Automatic fallback on failure
    - Unified async interface
    - Usage tracking
    """
    
    PROVIDERS = ["ollama", "claude"]
    
    def __init__(self):
        """Initialize LLM router."""
        self.default_provider = settings.default_llm_provider or "ollama"
        self.default_claude_model = settings.default_claude_model or "claude-3-5-haiku-20241022"
        self.enable_fallback = settings.enable_llm_fallback if hasattr(settings, 'enable_llm_fallback') else True
        
        # Initialize Ollama client on-demand
        self._ollama_client = None
        
        logger.info(
            f"LLMRouter initialized: default={self.default_provider}, "
            f"claude_model={self.default_claude_model}, fallback={self.enable_fallback}"
        )
    
    @property
    def ollama_client(self) -> Optional[OllamaClient]:
        """Get or create Ollama client."""
        if self._ollama_client is None:
            try:
                self._ollama_client = OllamaClient(
                    base_url=settings.ollama_base_url,
                    default_model=settings.ollama_model
                )
                if not self._ollama_client.test_connection():
                    logger.warning("Ollama client created but connection test failed")
                    self._ollama_client = None
            except Exception as e:
                logger.error(f"Failed to create Ollama client: {e}")
                self._ollama_client = None
        return self._ollama_client
    
    async def generate(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.2,
        system_prompt: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Generate text using specified or default provider.
        
        Args:
            prompt: User prompt (or complete prompt if no system_prompt)
            provider: "ollama" or "claude" (defaults to default_provider)
            model: Model name (provider-specific)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_prompt: System prompt (for Claude caching)
            
        Returns:
            Tuple of (generated_text, metadata_dict)
            metadata includes: provider, model, tokens, cost (if Claude)
        """
        provider = provider or self.default_provider
        provider = provider.lower()
        
        if provider not in self.PROVIDERS:
            logger.warning(f"Unknown provider '{provider}', defaulting to {self.default_provider}")
            provider = self.default_provider
        
        # Try primary provider
        response, metadata = await self._generate_with_provider(
            provider=provider,
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=system_prompt
        )
        
        if response is not None:
            return response, metadata
        
        # Fallback logic
        if self.enable_fallback:
            fallback_provider = "ollama" if provider == "claude" else "claude"
            logger.warning(f"Primary provider '{provider}' failed, trying fallback: {fallback_provider}")
            
            response, metadata = await self._generate_with_provider(
                provider=fallback_provider,
                prompt=prompt,
                model=None,  # Use default for fallback
                max_tokens=max_tokens,
                temperature=temperature,
                system_prompt=system_prompt
            )
            
            if response is not None:
                metadata["fallback_used"] = True
                metadata["original_provider"] = provider
                return response, metadata
        
        logger.error("All providers failed to generate response")
        return None, {"error": "All providers failed", "provider": provider}
    
    async def _generate_with_provider(
        self,
        provider: str,
        prompt: str,
        model: Optional[str],
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Generate using specific provider.
        
        Returns:
            Tuple of (response_text, metadata)
        """
        try:
            if provider == "claude":
                return await self._generate_claude(
                    prompt=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system_prompt=system_prompt
                )
            else:  # ollama
                return await self._generate_ollama(
                    prompt=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
        
        except Exception as e:
            logger.error(f"Error with provider '{provider}': {e}", exc_info=True)
            return None, None
    
    async def _generate_claude(
        self,
        prompt: str,
        model: Optional[str],
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Generate using Claude with prompt caching."""
        if not claude_service.is_available():
            logger.warning("Claude service not available")
            return None, None
        
        model = model or self.default_claude_model
        
        # Use caching if system prompt provided
        if system_prompt:
            response, usage_stats = await claude_service.generate_with_cache(
                system_prompt=system_prompt,
                user_prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
        else:
            response, usage_stats = await claude_service.generate(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
        
        if response is None:
            return None, None
        
        # Build metadata
        metadata = {
            "provider": "claude",
            "model": model,
            "usage": usage_stats or {},
            "cached": system_prompt is not None
        }
        
        return response, metadata
    
    async def _generate_ollama(
        self,
        prompt: str,
        model: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Generate using Ollama."""
        client = self.ollama_client
        if not client:
            logger.warning("Ollama service not available")
            return None, None
        
        # Ollama uses num_predict instead of max_tokens
        response = await client.generate_async(
            prompt=prompt,
            model=model,  # None uses default
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if response is None:
            return None, None
        
        # Build metadata (Ollama doesn't provide detailed usage stats)
        metadata = {
            "provider": "ollama",
            "model": model or client.default_model,
            "usage": {
                "estimated_tokens": len(response.split())  # Rough estimate
            }
        }
        
        return response, metadata
    
    def get_provider_status(self) -> Dict[str, Any]:
        """
        Get status of all providers.
        
        Returns:
            Dictionary with provider availability and stats
        """
        status = {
            "default_provider": self.default_provider,
            "fallback_enabled": self.enable_fallback,
            "providers": {}
        }
        
        # Ollama status
        ollama_available = False
        ollama_model = None
        client = self.ollama_client
        if client:
            try:
                ollama_available = client.test_connection()
                ollama_model = client.default_model
            except:
                pass
        
        status["providers"]["ollama"] = {
            "available": ollama_available,
            "model": ollama_model
        }
        
        # Claude status
        claude_available = claude_service.is_available()
        status["providers"]["claude"] = {
            "available": claude_available,
            "model": self.default_claude_model,
            "usage_stats": claude_service.get_usage_stats() if claude_available else None
        }
        
        return status
    
    def get_claude_usage(self) -> Dict[str, Any]:
        """Get Claude usage statistics."""
        return claude_service.get_usage_stats()
    
    def reset_claude_stats(self):
        """Reset Claude usage statistics."""
        claude_service.reset_stats()
    
    @staticmethod
    def list_available_models() -> Dict[str, Any]:
        """
        List all available models from all providers.
        
        Returns:
            Dictionary with models by provider
        """
        # Get Ollama default model from settings
        ollama_default = settings.ollama_model
        
        models = {
            "ollama": {
                "default": ollama_default,
                "models": [{"id": ollama_default, "name": ollama_default}]
            },
            "claude": {
                "default": "claude-3-5-haiku-20241022",
                "models": claude_service.list_models()
            }
        }
        
        return models


# Global instance
llm_router = LLMRouter()
