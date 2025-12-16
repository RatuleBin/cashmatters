"""
Script to check and create necessary Wagtail pages for production
Run this on your server with:
python manage.py shell < setup_pages.py
"""

from wagtail.models import Page, Site
from home.models import HomePage
from blog.models import NewsIndexPage

# Check existing pages
print("=" * 50)
print("EXISTING PAGES:")
print("=" * 50)
for page in Page.objects.all():
    print(f"ID: {page.id} | Type: {page.content_type} | Title: {page.title} | URL: {page.url_path}")

print("\n" + "=" * 50)
print("SITES:")
print("=" * 50)
for site in Site.objects.all():
    print(f"Site: {site.hostname}:{site.port} -> Root Page ID: {site.root_page.id} ({site.root_page.title})")

# Check if NewsIndexPage exists
news_pages = NewsIndexPage.objects.all()
print("\n" + "=" * 50)
print(f"NEWS INDEX PAGES: {news_pages.count()}")
print("=" * 50)
for news_page in news_pages:
    print(f"ID: {news_page.id} | Title: {news_page.title} | Slug: {news_page.slug} | URL: {news_page.url}")

print("\n" + "=" * 50)
print("INSTRUCTIONS:")
print("=" * 50)
print("1. If page ID 10 doesn't exist, you need to create it through the admin")
print("2. Go to: http://YOUR_IP/admin/")
print("3. Navigate to Pages and create the page structure you need")
print("4. Or use the page ID that exists instead of /10/")
