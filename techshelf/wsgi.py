"""
WSGI config for techshelf project.
"""

import os
from dotenv import load_dotenv
from django.core.wsgi import get_wsgi_application

# Load env variables for production
load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techshelf.settings')

application = get_wsgi_application()
