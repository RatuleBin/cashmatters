from django.core.management.base import BaseCommand
from blog.models import ArticleType, Location, Sector


class Command(BaseCommand):
    help = 'Populate categories for blog posts'

    def handle(self, *args, **options):
        # Article Types
        article_types = [
            'News',
            'Events',
            'Studies',
            'Key Fact',
            'Key Facts',
            'Podcast'
        ]

        for article_type in article_types:
            ArticleType.objects.get_or_create(name=article_type)
            self.stdout.write(f'Created/Found ArticleType: {article_type}')

        # Locations
        locations = [
            'Around the World',
            'Africa, Middle East & India',
            'Asia Pacific',
            'Europe',
            'Latin America & Caribbean',
            'The United States & Canada'
        ]

        for location in locations:
            Location.objects.get_or_create(name=location)
            self.stdout.write(f'Created/Found Location: {location}')

        # Sectors
        sectors = [
            'Cash is Freedom',
            'Cash is Fair',
            'Cash is Simple',
            'Cash is Friendly',
            'Cash is Resilient',
            'Cash is Common Sense',
            'Cash is Inclusive',
            'Cash is Private',
            'Cash is Secure'
        ]

        for sector in sectors:
            Sector.objects.get_or_create(name=sector)
            self.stdout.write(f'Created/Found Sector: {sector}')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated all categories!')
        )
