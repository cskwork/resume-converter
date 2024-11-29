import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ollama configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gemma2:latest')

# Available models
AVAILABLE_MODELS = [
    {'id': 'gemma2:latest', 'name': 'Gemma 2'},
    {'id': 'llama2:latest', 'name': 'Llama 2'},
    {'id': 'mistral:latest', 'name': 'Mistral'},
    {'id': 'qwen:latest', 'name': 'Qwen'},
    {'id': 'codellama:latest', 'name': 'Code Llama'},
    {'id': 'neural-chat:latest', 'name': 'Neural Chat'},
    {'id': 'qwq:latest', 'name': 'QWQ'},
]

# Model settings (can be expanded for model-specific configurations)
MODEL_SETTINGS = {
    'gemma2:latest': {
        'temperature': 0.7,
        'top_p': 0.9,
    },
    'llama2:latest': {
        'temperature': 0.7,
        'top_p': 0.9,
    },
    'mistral:latest': {
        'temperature': 0.7,
        'top_p': 0.9,
    },
    'qwen:latest': {
        'temperature': 0.7,
        'top_p': 0.9,
    },
    'codellama:latest': {
        'temperature': 0.7,
        'top_p': 0.9,
    },
    'neural-chat:latest': {
        'temperature': 0.7,
        'top_p': 0.9,
    },
    'qwq:latest': {
        'temperature': 0.7,
        'top_p': 0.9,
    },
}
