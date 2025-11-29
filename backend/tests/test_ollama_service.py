"""
Test Ollama service.
"""

import pytest
from app.services.ollama_service import OllamaClient


def test_ollama_client_initialization():
    """Test OllamaClient can be initialized."""
    client = OllamaClient(
        base_url="http://localhost:11434",
        default_model="gpt-oss:20b"
    )
    
    assert client.base_url == "http://localhost:11434"
    assert client.default_model == "gpt-oss:20b"


def test_extract_json():
    """Test JSON extraction from markdown code blocks."""
    client = OllamaClient()
    
    # Test with markdown code block
    text_with_markdown = '```json\n{"key": "value"}\n```'
    result = client._extract_json(text_with_markdown)
    assert result == '{"key": "value"}'
    
    # Test with plain JSON
    plain_json = '{"key": "value"}'
    result = client._extract_json(plain_json)
    assert result == '{"key": "value"}'
    
    # Test with just code block markers
    text_with_backticks = '```\n{"key": "value"}\n```'
    result = client._extract_json(text_with_backticks)
    assert result == '{"key": "value"}'


# Note: The following tests require Ollama to be running
# Mark them to skip if Ollama is not available

@pytest.mark.skipif(not pytest.config.getoption("--run-ollama"), 
                    default=True,
                    reason="Requires Ollama server running")
def test_ollama_connection():
    """Test connection to Ollama server."""
    client = OllamaClient()
    is_connected = client.test_connection()
    assert is_connected is True


@pytest.mark.skipif(not pytest.config.getoption("--run-ollama"),
                    default=True,
                    reason="Requires Ollama server running")
def test_ollama_generation():
    """Test basic text generation."""
    client = OllamaClient()
    response = client.generate("Say hello")
    
    assert isinstance(response, str)
    assert len(response) > 0
