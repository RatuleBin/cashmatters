#!/usr/bin/env python
"""Clean up orphaned WhyCashMattersFeaturePage records"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashmatters.settings.dev')
django.setup()

from wagtail.models import Page
from django.contrib.contenttypes.models import ContentType
from django.db import connection

# Find the content type for WhyCashMattersFeaturePage
try:
    ct = ContentType.objects.get(app_label='blog', model='whycashmattersfeaturepage')
    print(f"Found content type: {ct}")
    
    # Find all pages with this content type
    pages = Page.objects.filter(content_type=ct)
    print(f"\nFound {pages.count()} page(s) with this content type:")
    
    for page in pages:
        print(f"  ID: {page.id}, Title: {page.title}, Slug: {page.slug}")
    
    if pages.exists():
        print("\nDeleting orphaned pages using raw SQL...")
        with connection.cursor() as cursor:
            for page in pages:
                # Delete related records first (try each, some tables may not exist)
                tables_to_clean = [
                    "wagtailcore_pagesubscription",
                    "wagtailcore_pagelogentry",
                    "wagtailcore_revision",
                    "wagtailcore_grouppagemission",
                ]
                for table in tables_to_clean:
                    try:
                        cursor.execute(f"DELETE FROM {table} WHERE page_id = %s", [page.id])
                    except Exception:
                        pass  # Table might not exist or no records
                
                # Delete from wagtailcore_page table
                cursor.execute("DELETE FROM wagtailcore_page WHERE id = %s", [page.id])
                print(f"Deleted page {page.id} from database")
        print(f"\nDeleted {pages.count()} page(s) total!")
    else:
        print("No pages to delete.")
        
except ContentType.DoesNotExist:
    print("WhyCashMattersFeaturePage content type not found.")
