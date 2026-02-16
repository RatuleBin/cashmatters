from django.core.management.base import BaseCommand
from wagtail.models import Page, Site
from home.models import HomePage
from blog.models import SupportPage, WhyCashMattersPage, BlogIndexPage


class Command(BaseCommand):
    help = 'Create essential pages: HomePage, SupportPage, and WhyCashMattersPage'

    def handle(self, *args, **options):
        # Get the root page
        try:
            root_page = Page.objects.get(id=1)  # Wagtail's root page
        except Page.DoesNotExist:
            self.stdout.write(self.style.ERROR('Root page does not exist'))
            return

        # Check if HomePage exists
        try:
            home_page = HomePage.objects.live().first()
            if home_page:
                self.stdout.write(f'HomePage already exists: {home_page.title}')
            else:
                # Create HomePage using Wagtail's method
                home_page = HomePage(title='Home', slug='home')
                root_page.add_child(instance=home_page)
                home_page.save_revision().publish()
                self.stdout.write(f'Created HomePage: {home_page.title}')

                # Set as default site homepage
                site = Site.objects.get(id=1)
                site.root_page = home_page
                site.save()
                self.stdout.write('Set HomePage as default site homepage')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error with HomePage: {e}'))
            import traceback
            traceback.print_exc()
            return

        # Create SupportPage if it doesn't exist
        try:
            support_page = SupportPage.objects.live().first()
            if support_page:
                self.stdout.write(f'SupportPage already exists: {support_page.title}')
            else:
                support_page = SupportPage(
                    title='Support Cash',
                    slug='support',
                    page_header_title='Support Cash',
                    description_title='Support Our Work',
                    description_content='<p>Join us in preserving payment choice and supporting the continued availability of cash.</p>',
                    introduction='<p>Cash is essential for financial inclusion and privacy. Support our efforts to ensure cash remains a viable payment option.</p>',
                )
                home_page.add_child(instance=support_page)
                self.stdout.write(f'Created SupportPage: {support_page.title}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating SupportPage: {e}'))

        # Create WhyCashMattersPage if it doesn't exist
        try:
            why_page = WhyCashMattersPage.objects.live().first()
            if why_page:
                self.stdout.write(f'WhyCashMattersPage already exists: {why_page.title}')
            else:
                why_page = WhyCashMattersPage(
                    title='Why Cash Matters',
                    slug='why-cash-matters',
                    date='2025-12-19',
                    intro='Understanding the importance of cash in our society',
                    body='[]',  # Empty streamfield
                    facts='[]',  # Empty streamfield
                )
                home_page.add_child(instance=why_page)
                self.stdout.write(f'Created WhyCashMattersPage: {why_page.title}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating WhyCashMattersPage: {e}'))

        # Create BlogIndexPage if it doesn't exist
        try:
            blog_index = BlogIndexPage.objects.live().first()
            if blog_index:
                self.stdout.write(f'BlogIndexPage already exists: {blog_index.title}')
            else:
                blog_index = BlogIndexPage(
                    title='Blog',
                    slug='blog',
                    intro='Latest blog posts and articles',
                )
                home_page.add_child(instance=blog_index)
                blog_index.save_revision().publish()
                self.stdout.write(f'Created BlogIndexPage: {blog_index.title}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating BlogIndexPage: {e}'))

        self.stdout.write(self.style.SUCCESS('Essential pages setup complete!'))