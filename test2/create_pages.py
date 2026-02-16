#!/usr/bin/env python3
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashmatters.settings.dev')
django.setup()

from wagtail.models import Page, Site
from home.models import HomePage
from blog.models import SupportPage, WhyCashMattersPage
from datetime import date

def create_pages():
    # Get root page
    root_page = Page.objects.get(id=1)

    # Create HomePage if it doesn't exist
    home_page = HomePage.objects.live().first()
    if not home_page:
        print("Creating HomePage...")
        home_page = HomePage(title='Home', slug='home')
        # For the first child of root, we need to set the path manually
        home_page.path = '00010001'
        home_page.depth = 2
        home_page.numchild = 0
        home_page.save()
        home_page.save_revision().publish()

        # Set as default site homepage
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'hostname': 'localhost',
                'port': 80,
                'site_name': 'Cash Matters',
                'root_page': home_page
            }
        )
        if created:
            print("Site created")
        else:
            site.root_page = home_page
            site.save()
            print("Site updated with HomePage")
    else:
        print(f"HomePage already exists: {home_page.title}")

    # Create SupportPage if it doesn't exist
    support_page = SupportPage.objects.live().first()
    if not support_page:
        print("Creating SupportPage...")
        support_page = SupportPage(
            title='Support Cash',
            slug='support',
            page_header_title='Support Cash',
            description_title='Support Our Work',
            description_content='<p>Join us in preserving payment choice and supporting the continued availability of cash.</p>',
            introduction='<p>Cash is essential for financial inclusion and privacy. Support our efforts to ensure cash remains a viable payment option.</p>',
        )
        home_page.add_child(instance=support_page)
        support_page.save_revision().publish()
        print("SupportPage created")
    else:
        print(f"SupportPage already exists: {support_page.title}")

    # Create WhyCashMattersPage if it doesn't exist
    why_page = WhyCashMattersPage.objects.live().first()
    if not why_page:
        print("Creating WhyCashMattersPage...")
        why_page = WhyCashMattersPage(
            title='Why Cash Matters',
            slug='why-cash-matters',
            date=date.today(),
            intro='Understanding the importance of cash in our society',
            body='[]',
            facts='[]',
        )
        home_page.add_child(instance=why_page)
        why_page.save_revision().publish()
        print("WhyCashMattersPage created")
    else:
        print(f"WhyCashMattersPage already exists: {why_page.title}")

    print("All essential pages created successfully!")

if __name__ == '__main__':
    create_pages()