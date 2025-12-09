"""
Claude API service with prompt caching, retry logic, and cost tracking.
Production-grade implementation for Anthropic Claude integration.
"""

import asyncio
import json
from typing import Optional, Dict, Any, Tuple
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
        "claude-4.5-haiku-20250514": {
            "input": 0.40,
            "input_cached": 0.04,  # 90% discount
            "output": 1.60
        },
        "claude-3-5-haiku-20241022": {
            "input": 0.25,
            "input_cached": 0.025,  # 90% discount
            "output": 1.25
        },
        "claude-4.5-sonnet-20250514": {
            "input": 3.00,
            "input_cached": 0.30,  # 90% discount
            "output": 15.00
        },
        "claude-3-5-sonnet-20241022": {
            "input": 3.00,
            "input_cached": 0.30,  # 90% discount
            "output": 15.00
        },
        "claude-opus-4-20250514": {
            "input": 15.00,
            "input_cached": 1.50,  # 90% discount
            "output": 75.00
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
        pricing = self.PRICING.get(model, self.PRICING["claude-4.5-haiku-20250514"])
        
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
        return {
            "total_requests": self.request_count,
            "total_input_tokens": self.total_input_tokens,
            "total_cached_tokens": self.total_cached_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost": round(self.total_cost, 4),
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
    
    # Available models
    MODELS = {
        "claude-4.5-haiku": "claude-4.5-haiku-20250514",
        "claude-3.5-haiku": "claude-3-5-haiku-20241022",
        "claude-4.5-sonnet": "claude-4.5-sonnet-20250514",
        "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",
        "claude-opus-4": "claude-opus-4-20250514"
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "claude-4.5-haiku",
        max_retries: int = 3,
        timeout: int = 60
    ):
        """
        Initialize Claude service.
        
        Args:
            api_key: Anthropic API key (defaults to settings)
            default_model: Default model to use
            max_retries: Maximum retry attempts
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or settings.claude_api_key
        self.default_model = self.MODELS.get(default_model, self.MODELS["claude-4.5-haiku"])
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
            logger.info(f"ClaudeService initialized with model: {self.default_model}")
        
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
        
        model_name = self.MODELS.get(model, self.default_model)
        
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
    def list_models() -> Dict[str, Dict[str, Any]]:
        """
        Get list of available models with metadata.
        
        Returns:
            Dictionary of model info
        """
        return {
            "claude-4.5-haiku": {
                "name": "Claude 4.5 Haiku",
                "version": "claude-4.5-haiku-20250514",
                "description": "Fastest and most cost-effective (Recommended)",
                "speed": "fastest",
                "cost": "lowest",
                "quality": "good"
            },
            "claude-3.5-haiku": {
                "name": "Claude 3.5 Haiku",
                "version": "claude-3-5-haiku-20241022",
                "description": "Previous generation fast model",
                "speed": "fastest",
                "cost": "lowest",
                "quality": "good"
            },
            "claude-4.5-sonnet": {
                "name": "Claude 4.5 Sonnet",
                "version": "claude-4.5-sonnet-20250514",
                "description": "Balanced quality and speed",
                "speed": "medium",
                "cost": "medium",
                "quality": "excellent"
            },
            "claude-3.5-sonnet": {
                "name": "Claude 3.5 Sonnet",
                "version": "claude-3-5-sonnet-20241022",
                "description": "Previous generation balanced model",
                "speed": "medium",
                "cost": "medium",
                "quality": "excellent"
            },
            "claude-opus-4": {
                "name": "Claude Opus 4",
                "version": "claude-opus-4-20250514",
                "description": "Highest quality, most expensive",
                "speed": "slower",
                "cost": "highest",
                "quality": "best"
            }
        }


# Global instance
claude_service = ClaudeService()
