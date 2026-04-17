import sys
import os

# Add the project root to Python's path so that "app" can be found
# When Vercel runs api/index.py, the working directory may not include the root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
