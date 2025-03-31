"""
ASGI config for techshelf project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techshelf.settings')

application = get_asgi_application()
