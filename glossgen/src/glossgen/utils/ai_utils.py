import os
from typing import Tuple, Dict, Any, Optional
import requests
import json

from glossgen.config.app_config import AppConfig

def test_ai_connection(
    provider: str, 
    api_key: str, 
    model: str, 
    endpoint: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Test connection to the AI provider API
    
    Args:
        provider: AI provider name
        api_key: API key
        model: Model name
        endpoint: Custom endpoint URL (for OpenAI Compatible)
        
    Returns:
        Tuple of (success, message)
    """
    # If no API key provided, try to get from environment
    if not api_key:
        config = AppConfig()
        env_key_name = config.ENV_API_KEYS.get(provider, "")
        api_key = os.environ.get(env_key_name, "")
        
        if not api_key:
            return False, f"No API key provided and no environment variable {env_key_name} found"
    
    try:
        if provider == "OpenAI" or provider == "OpenAI Compatible":
            return _test_openai_connection(api_key, model, endpoint)
        elif provider == "Deepseek":
            return _test_deepseek_connection(api_key, model)
        elif provider == "Claude":
            return _test_claude_connection(api_key, model)
        elif provider == "Google Gemini":
            return _test_gemini_connection(api_key, model)
        else:
            return False, f"Unsupported provider: {provider}"
    except Exception as e:
        return False, f"Error testing connection: {str(e)}"

def _test_openai_connection(
    api_key: str, 
    model: str, 
    endpoint: Optional[str] = None
) -> Tuple[bool, str]:
    """Test connection to OpenAI or OpenAI-compatible API"""
    import openai
    
    client = openai.OpenAI(
        api_key=api_key,
        base_url=endpoint or "https://api.openai.com/v1"
    )
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hello, are you working?"}],
            max_tokens=10
        )
        return True, f"Successfully connected to {model}"
    except Exception as e:
        return False, f"Failed to connect: {str(e)}"

def _test_deepseek_connection(api_key: str, model: str) -> Tuple[bool, str]:
    """Test connection to Deepseek API"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": "Hello, are you working?"}],
        "max_tokens": 10
    }
    
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        return True, f"Successfully connected to {model}"
    else:
        return False, f"Failed to connect: {response.text}"

def _test_claude_connection(api_key: str, model: str) -> Tuple[bool, str]:
    """Test connection to Anthropic Claude API"""
    import anthropic
    
    client = anthropic.Anthropic(api_key=api_key)
    
    try:
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hello, are you working?"}]
        )
        return True, f"Successfully connected to {model}"
    except Exception as e:
        return False, f"Failed to connect: {str(e)}"

def _test_gemini_connection(api_key: str, model: str) -> Tuple[bool, str]:
    """Test connection to Google Gemini API"""
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    try:
        chat = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key
        )
        response = chat.invoke("Hello, are you working?")
        return True, f"Successfully connected to {model}"
    except Exception as e:
        return False, f"Failed to connect: {str(e)}"

def get_llm_client(
    provider: str, 
    api_key: str, 
    model: str, 
    endpoint: Optional[str] = None,
    temperature: float = 0.2
) -> Any:
    """
    Get the appropriate LLM client based on provider
    
    Args:
        provider: AI provider name
        api_key: API key
        model: Model name
        endpoint: Custom endpoint URL (for OpenAI Compatible)
        temperature: Temperature setting for generation
        
    Returns:
        LLM client object
    """
    # Use environment variable if no API key provided
    if not api_key:
        config = AppConfig()
        env_key_name = config.ENV_API_KEYS.get(provider, "")
        api_key = os.environ.get(env_key_name, "")
    
    if provider == "OpenAI" or provider == "OpenAI Compatible":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model_name=model,
            temperature=temperature,
            openai_api_key=api_key,
            openai_api_base=endpoint
        )
    elif provider == "Deepseek":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model_name=model,
            temperature=temperature,
            openai_api_key=api_key,
            openai_api_base="https://api.deepseek.com/v1"
        )
    elif provider == "Claude":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model_name=model,
            temperature=temperature,
            anthropic_api_key=api_key
        )
    elif provider == "Google Gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=api_key
        )
    else:
        # Default to OpenAI
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=temperature,
            openai_api_key=api_key
        ) 