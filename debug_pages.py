#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashmatters.settings.dev')
django.setup()

from wagtail.models import Page
from home.models import HomePage
from blog.models import SupportPage, WhyCashMattersPage

print('=== Page Status Check ===')
print('HomePage exists:', HomePage.objects.exists())
print('SupportPage exists:', SupportPage.objects.exists())
print('WhyCashMattersPage exists:', WhyCashMattersPage.objects.exists())

print('\n=== All Pages ===')
for p in Page.objects.all():
    print(f'  {p.id}: {p.title} ({p.slug}) - {p.__class__.__name__} - path: {p.path}')

print('\n=== HomePage Details ===')
try:
    home_page = HomePage.objects.first()
    if home_page:
        print(f'ID: {home_page.id}')
        print(f'Title: {home_page.title}')
        print(f'Slug: {home_page.slug}')
        print(f'Path: {home_page.path}')
        print(f'Depth: {home_page.depth}')
        print(f'Live: {home_page.live}')
    else:
        print('No HomePage found')
except Exception as e:
    print(f'Error getting HomePage: {e}')

print('\n=== Root Page ===')
try:
    root = Page.objects.get(id=1)
    print(f'ID: {root.id}')
    print(f'Title: {root.title}')
    print(f'Path: {root.path}')
    print(f'Depth: {root.depth}')
except Exception as e:
    print(f'Error getting root page: {e}')