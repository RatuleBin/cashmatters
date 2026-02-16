#!/usr/bin/env python
import os
import django
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashmatters.settings.dev')

# Setup Django
django.setup()

from blog.models import WhyCashMattersPage

print('Existing WhyCashMattersPage count:', WhyCashMattersPage.objects.count())
if WhyCashMattersPage.objects.exists():
    page = WhyCashMattersPage.objects.first()
    print('Page ID:', page.id)
    print('Page title:', page.title)
    print('Page slug:', page.slug)
else:
    print('No WhyCashMattersPage exists yet')