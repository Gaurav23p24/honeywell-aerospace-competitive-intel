"""
Environment configuration loader
Handles API keys and environment variables
"""

import os
from typing import Optional

def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def get_api_key(service: str) -> Optional[str]:
    """Get API key for a service"""
    key_map = {
        'openai': 'OPENAI_API_KEY',
        'tavily': 'TAVILY_API_KEY', 
        'skyvern': 'SKYVERN_API_KEY',
        'langsmith': 'LANGSMITH_API_KEY'
    }
    
    env_key = key_map.get(service.lower())
    if env_key:
        return os.getenv(env_key)
    return None

def check_api_keys() -> dict:
    """Check which API keys are available"""
    services = ['openai', 'tavily', 'skyvern', 'langsmith']
    available = {}
    
    for service in services:
        key = get_api_key(service)
        available[service] = key is not None
        
    return available

# Load environment on import
load_env_file()

# Example usage
if __name__ == "__main__":
    print("API Key Availability Check:")
    available = check_api_keys()
    
    for service, has_key in available.items():
        status = "Available" if has_key else "Missing"
        print(f"{service.upper()}: {status}")
    
    if not any(available.values()):
        print("\nNo API keys found. Create a .env file using env_template.txt")
