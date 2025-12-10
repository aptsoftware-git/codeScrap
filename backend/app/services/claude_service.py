"""
Claude API service with prompt caching, retry logic, and cost tracking.
Production-grade implementation for Anthropic Claude integration.
"""

import asyncio
import json
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime
from loguru import logger
import anthropic
from anthropic import AsyncAnthropic
from anthropic.types import Message, Usage

from app.settings import settings


class ClaudeUsageStats:
    """Track Claude API usage and costs."""
    
    # Pricing per 1M tokens (as of Dec 2024)
    PRICING = {
        "claude-3-5-haiku-20241022": {
            "input": 0.80,
            "input_cached": 0.08,
            "output": 4.00
        },
        "claude-3-haiku-20240307": {
            "input": 0.25,
            "input_cached": 0.025,
            "output": 1.25
        },
        "claude-3-5-sonnet-20241022": {
            "input": 3.00,
            "input_cached": 0.30,
            "output": 15.00
        },
        "claude-3-5-sonnet-20240620": {
            "input": 3.00,
            "input_cached": 0.30,
            "output": 15.00
        },
        "claude-3-opus-20240229": {
            "input": 15.00,
            "input_cached": 1.50,
            "output": 75.00
        },
        "claude-3-sonnet-20240229": {
            "input": 3.00,
            "input_cached": 0.30,
            "output": 15.00
        }
    }
    
    def __init__(self):
        self.total_input_tokens = 0
        self.total_cached_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.request_count = 0
        self.last_reset = datetime.now()
    
    def add_usage(self, usage: Usage, model: str) -> Dict[str, Any]:
        """
        Add usage statistics and calculate cost.
        
        Args:
            usage: Anthropic Usage object
            model: Model name used
            
        Returns:
            Dictionary with cost breakdown
        """
        pricing = self.PRICING.get(model, self.PRICING["claude-3-5-haiku-20241022"])
        
        # Extract tokens
        input_tokens = usage.input_tokens or 0
        cached_tokens = getattr(usage, 'cache_read_input_tokens', 0) or 0
        output_tokens = usage.output_tokens or 0
        
        # Calculate costs (per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        cached_cost = (cached_tokens / 1_000_000) * pricing["input_cached"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + cached_cost + output_cost
        
        # Update totals
        self.total_input_tokens += input_tokens
        self.total_cached_tokens += cached_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += total_cost
        self.request_count += 1
        
        return {
            "input_tokens": input_tokens,
            "cached_tokens": cached_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + cached_tokens + output_tokens,
            "input_cost": round(input_cost, 6),
            "cached_cost": round(cached_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "cache_hit_rate": round((cached_tokens / (input_tokens + cached_tokens)) * 100, 1) if (input_tokens + cached_tokens) > 0 else 0
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get usage summary statistics."""
        # Calculate cache savings (90% discount on cached tokens)
        # What we paid for cached tokens
        cached_cost = self.total_cached_tokens * 0.00000025  # Average cached rate
        # What we would have paid without caching
        full_cost = self.total_cached_tokens * 0.0000025  # Average full rate
        cache_savings = full_cost - cached_cost
        
        return {
            "total_requests": self.request_count,
            "total_input_tokens": self.total_input_tokens,
            "total_cached_tokens": self.total_cached_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost": round(self.total_cost, 4),
            "cache_savings": round(cache_savings, 4),
            "average_cost_per_request": round(self.total_cost / self.request_count, 6) if self.request_count > 0 else 0,
            "cache_hit_rate": round((self.total_cached_tokens / (self.total_input_tokens + self.total_cached_tokens)) * 100, 1) if (self.total_input_tokens + self.total_cached_tokens) > 0 else 0,
            "since": self.last_reset.isoformat()
        }
    
    def reset(self):
        """Reset statistics."""
        self.__init__()


class ClaudeService:
    """
    Production-grade Claude API service with:
    - Prompt caching for cost optimization
    - Exponential backoff retry logic
    - Rate limit handling
    - Token usage tracking
    - Async operation with queue management
    """
    
    # Available models - using full model names directly
    MODELS = {
        # Full model names (used directly)
        "claude-3-5-haiku-20241022": "claude-3-5-haiku-20241022",
        "claude-3-haiku-20240307": "claude-3-haiku-20240307",
        "claude-3-5-sonnet-20241022": "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620": "claude-3-5-sonnet-20240620",
        "claude-3-opus-20240229": "claude-3-opus-20240229",
        "claude-3-sonnet-20240229": "claude-3-sonnet-20240229",
        # Short name aliases for backward compatibility
        "claude-3.5-haiku": "claude-3-5-haiku-20241022",
        "claude-3-haiku": "claude-3-haiku-20240307",
        "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229"
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "claude-3-5-haiku-20241022",  # Use full model name
        max_retries: int = 3,
        timeout: int = 60
    ):
        """
        Initialize Claude service.
        
        Args:
            api_key: Anthropic API key (defaults to settings)
            default_model: Default model to use (short name like 'claude-3.5-haiku')
            max_retries: Maximum retry attempts
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or settings.claude_api_key
        # Store default model, fallback to fastest model if invalid
        self.default_model = default_model if default_model in self.MODELS else "claude-3-5-haiku-20241022"
        self.max_retries = max_retries
        self.timeout = timeout
        
        if not self.api_key:
            logger.warning("Claude API key not configured")
            self.client = None
        else:
            self.client = AsyncAnthropic(
                api_key=self.api_key,
                timeout=timeout
            )
            # Log with resolved full model name
            logger.info(f"ClaudeService initialized with model: {self.MODELS[self.default_model]}")
        
        # Usage tracking
        self.usage_stats = ClaudeUsageStats()
        
        # Queue for rate limiting
        self.semaphore = asyncio.Semaphore(settings.claude_max_concurrent or 5)
    
    def is_available(self) -> bool:
        """Check if Claude service is available."""
        return self.client is not None
    
    async def generate_with_cache(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.2
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Generate response with prompt caching.
        
        The system_prompt is cached for reuse across requests.
        
        Args:
            system_prompt: System instructions (will be cached)
            user_prompt: User message (varies per request)
            model: Model to use (defaults to default_model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Tuple of (generated_text, usage_stats) or (None, None) on failure
        """
        if not self.is_available():
            logger.error("Claude service not available")
            return None, None
        
        # Resolve model name: if model is provided, look it up; otherwise use default
        # First get the short model name (what user passes)
        model_key = model or self.default_model
        # Then resolve to full API model name
        model_name = self.MODELS.get(model_key, self.MODELS[self.default_model])
        
        async with self.semaphore:  # Rate limiting
            for attempt in range(self.max_retries):
                try:
                    # Use prompt caching for system message
                    message = await self.client.messages.create(
                        model=model_name,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        system=[
                            {
                                "type": "text",
                                "text": system_prompt,
                                "cache_control": {"type": "ephemeral"}  # Enable caching
                            }
                        ],
                        messages=[
                            {
                                "role": "user",
                                "content": user_prompt
                            }
                        ]
                    )
                    
                    # Extract response
                    response_text = message.content[0].text if message.content else None
                    
                    # Track usage
                    usage_info = self.usage_stats.add_usage(message.usage, model_name)
                    
                    logger.info(
                        f"Claude API success: {usage_info['total_tokens']} tokens, "
                        f"${usage_info['total_cost']:.6f}, "
                        f"cache hit: {usage_info['cache_hit_rate']}%"
                    )
                    
                    return response_text, usage_info
                
                except anthropic.RateLimitError as e:
                    wait_time = (2 ** attempt) * 2  # Exponential backoff: 2s, 4s, 8s
                    logger.warning(f"Claude rate limit hit, attempt {attempt + 1}/{self.max_retries}, waiting {wait_time}s: {e}")
                    
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error("Claude rate limit exceeded, max retries reached")
                        return None, None
                
                except anthropic.APITimeoutError as e:
                    logger.error(f"Claude API timeout on attempt {attempt + 1}/{self.max_retries}: {e}")
                    if attempt == self.max_retries - 1:
                        return None, None
                    await asyncio.sleep(2)
                
                except anthropic.APIError as e:
                    logger.error(f"Claude API error on attempt {attempt + 1}/{self.max_retries}: {e}")
                    if attempt == self.max_retries - 1:
                        return None, None
                    await asyncio.sleep(1)
                
                except Exception as e:
                    logger.error(f"Unexpected error calling Claude API: {e}", exc_info=True)
                    return None, None
        
        return None, None
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.2
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Generate response without caching (simple mode).
        
        Args:
            prompt: Complete prompt
            model: Model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Tuple of (generated_text, usage_stats) or (None, None) on failure
        """
        # Use empty system and put everything in user message
        return await self.generate_with_cache(
            system_prompt="",
            user_prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        return self.usage_stats.get_summary()
    
    def reset_stats(self):
        """Reset usage statistics."""
        self.usage_stats.reset()
        logger.info("Claude usage statistics reset")
    
    @staticmethod
    def list_models() -> List[Dict[str, Any]]:
        """
        Get list of available models with metadata.
        
        Returns:
            List of model info dictionaries
        """
        # Return models in the same format as old implementation
        return [
            {
                "id": "claude-3-5-haiku-20241022",
                "name": "Claude 3.5 Haiku (Fastest)",
                "description": "Fastest and most cost-effective",
                "speed": "fastest",
                "cost": "lowest"
            },
            {
                "id": "claude-3-haiku-20240307",
                "name": "Claude 3 Haiku",
                "description": "Fast and affordable",
                "speed": "fastest",
                "cost": "lowest"
            },
            {
                "id": "claude-3-5-sonnet-20241022",
                "name": "Claude 3.5 Sonnet (Latest)",
                "description": "Latest balanced model",
                "speed": "medium",
                "cost": "medium"
            },
            {
                "id": "claude-3-5-sonnet-20240620",
                "name": "Claude 3.5 Sonnet",
                "description": "Balanced quality and speed",
                "speed": "medium",
                "cost": "medium"
            },
            {
                "id": "claude-3-opus-20240229",
                "name": "Claude 3 Opus (Best Quality)",
                "description": "Highest quality, most expensive",
                "speed": "slower",
                "cost": "highest"
            },
            {
                "id": "claude-3-sonnet-20240229",
                "name": "Claude 3 Sonnet",
                "description": "Balanced model",
                "speed": "medium",
                "cost": "medium"
            }
        ]


# Global instance
claude_service = ClaudeService()
