import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
import os

def get_text_model_instance():
    load_dotenv()
    
    # Check for OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # Check for Anthropic API key
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    # Determine which API to use based on available keys
    if anthropic_api_key:
        print("Using Anthropic API")
        try:
            # Get Claude model name from env or use default
            model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
            
            # Set Anthropic API key as environment variable
            # This is likely how PydanticAI expects to find it
            os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key
            
            # Initialize the model with just the model name
            return AnthropicModel(
                model_name=model_name
            )
        except Exception as e:
            print(f"Failed to initialize Anthropic model: {str(e)}")
            # If Anthropic fails but OpenAI key is available, fall back to OpenAI
            if openai_api_key:
                print("Falling back to OpenAI API")
            else:
                raise Exception(f"Anthropic initialization failed and no OpenAI fallback available: {str(e)}")
    
    # Use OpenAI if Anthropic not available or as fallback
    if openai_api_key:
        print("Using OpenAI API")
        try:
            # Initialize the model with just the model name and let it handle the API client
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-2024-08-06")
            
            return OpenAIModel(
                model_name=model_name,
                # No client or openai_client parameter needed
            )
        except Exception as e:
            raise Exception(f"Failed to initialize OpenAI model: {str(e)}")
    
    # If we get here and have no API keys, raise an error
    raise ValueError("No API keys found. Please provide either OPENAI_API_KEY or ANTHROPIC_API_KEY in environment variables.")