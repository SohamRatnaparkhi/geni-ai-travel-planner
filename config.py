"""
Configuration file for AI models and settings
"""

# AI Model configurations
MODELS = {
    "gemini": {
        "text": "gemini-2.5-flash",
        "image": "gemini-2.5-flash-image-preview",  # For image generation
    },
    "perplexity": {
        "text": "sonar",
    }
}

# API Settings
GEMINI_SETTINGS = {
    "temperature": {
        "text": 0.35,
        "image": 0.7,
    },
    "top_p": {
        "text": 0.9,
        "image": 0.95,
    },
    "max_output_tokens": {
        "text": 40960,
        "image": 2048,
    },
    "timeout": {
        "text": 120,
        "image": 60,
    }
}

PERPLEXITY_SETTINGS = {
    "temperature": 0.2,
    "top_p": 0.9,
    "max_tokens": 1400,
    "web_search_options": {"search_context_size": "high"},
}

# Image Generation Settings
IMAGE_GENERATION = {
    "max_images_per_entity": 2,
    "image_quality": "standard",
    "image_size": "1024x1024",
}
