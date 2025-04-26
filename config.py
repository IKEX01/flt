import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Proxy configuration
PROXY = os.getenv('PROXY', '')

# Server configuration
FLASK_RUN_HOST = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
FLASK_RUN_PORT = int(os.getenv('FLASK_RUN_PORT', 5000))
