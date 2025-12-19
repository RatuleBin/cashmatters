#!/usr/bin/env python
import os
import django
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashmatters.settings.dev')

# Setup Django
django.setup()

import wagtail.admin.views.pages as pages
print('Available in wagtail.admin.views.pages:')
for attr in dir(pages):
    if not attr.startswith('_'):
        print(f'  {attr}')

# Try to find the create view
try:
    from wagtail.admin.views.pages import create
    print(f'create function: {create}')
except ImportError as e:
    print(f'Import error for create: {e}')

# Check the create module
from wagtail.admin.views.pages import create as create_module
print('Available in create module:')
for attr in dir(create_module):
    if not attr.startswith('_'):
        print(f'  {attr}')

# Try to find the view class
if hasattr(create_module, 'CreateView'):
    print('CreateView found in create module')
else:
    print('CreateView not found in create module')