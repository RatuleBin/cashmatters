#!/usr/bin/env python
import os
import django
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashmatters.settings.dev')

# Setup Django
django.setup()

from django.urls import resolve

# Test the custom clean URLs
test_urls = [
    '/admin/why-cash-matters/',
    '/admin/support/',
]

for url in test_urls:
    try:
        match = resolve(url)
        print(f'URL: {url}')
        print('Resolved URL:', match)
        print('View function:', match.func)
        print('URL name:', match.url_name)
        print('Args:', match.args)
        print('Kwargs:', match.kwargs)
        print('---')
    except Exception as e:
        print(f'Error resolving {url}: {e}')
        print('---')