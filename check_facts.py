#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashmatters.settings.dev')
django.setup()

from blog.models import WhyCashMattersPage

# Check if page exists and has facts
page = WhyCashMattersPage.objects.first()
print(f'Page exists: {page is not None}')
if page:
    print(f'Page title: {page.title}')
    print(f'Page live: {page.live}')
    print(f'Page pk: {page.pk}')
    print(f'Facts count: {len(page.facts) if page.facts else 0}')

# Check live pages
live_pages = WhyCashMattersPage.objects.live()
print(f'Live pages count: {live_pages.count()}')
for live_page in live_pages:
    print(f'Live page: {live_page.title}, pk: {live_page.pk}')
