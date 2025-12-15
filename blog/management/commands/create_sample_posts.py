from django.core.management.base import BaseCommand
from django.utils import timezone
from wagtail.models import Page
from blog.models import (NewsIndexPage, ArticlePage, ArticleType,
                         Location, Sector)


class Command(BaseCommand):
    help = 'Create sample blog posts for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='Number of sample posts to create',
        )

    def handle(self, *args, **options):
        count = options['count']

        # Get or create the NewsIndexPage
        try:
            news_index = NewsIndexPage.objects.get(slug='news')
            self.stdout.write(f'Found NewsIndexPage: {news_index.title}')
        except NewsIndexPage.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    'NewsIndexPage with slug "news" not found. '
                    'Please create it first.'
                )
            )
            return

        # Get or create categories
        news_type, _ = ArticleType.objects.get_or_create(name='News')
        global_location, _ = Location.objects.get_or_create(
            name='Around the World'
        )
        freedom_sector, _ = Sector.objects.get_or_create(
            name='Cash is Freedom'
        )

        # Sample blog post data
        sample_posts = [
            {
                'title': 'The Future of Digital Payments',
                'intro': ('Exploring how digital payments are evolving and '
                          'what it means for traditional cash systems.'),
                'body': '''
                <p>Digital payments have revolutionized the way we handle
                transactions in recent years. From mobile wallets to
                cryptocurrency, the landscape is constantly changing.</p>

                <p>However, traditional cash remains a cornerstone of financial
                inclusion, providing privacy, security, and accessibility that
                digital systems often struggle to match.</p>

                <p>This article explores the current state of digital payments
                and their coexistence with physical currency in modern
                economies.</p>
                ''',
                'date': timezone.now().date(),
            },
            {
                'title': 'Cash vs Digital: Privacy Considerations',
                'intro': ('An in-depth look at privacy implications of cash '
                          'versus digital payment methods.'),
                'body': '''
                <p>Privacy is becoming an increasingly important consideration in financial transactions. While digital payments offer convenience and traceability, they also raise significant privacy concerns.</p>

                <p>Cash transactions, by their very nature, provide a level of anonymity that digital systems cannot match without additional privacy-preserving technologies.</p>

                <p>This post examines the privacy trade-offs between different payment methods and their implications for consumers and businesses.</p>
                ''',
                'date': timezone.now().date(),
            },
            {
                'title': 'Financial Inclusion Through Cash',
                'intro': 'How cash continues to play a vital role in ensuring financial access for underserved populations.',
                'body': '''
                <p>Financial inclusion remains a global challenge, with millions of people still excluded from formal banking systems. Cash plays a crucial role in bridging this gap.</p>

                <p>While digital solutions promise greater efficiency, they often require infrastructure and literacy that many communities lack. Cash provides a universal, accessible alternative.</p>

                <p>Learn about initiatives and strategies that leverage cash to promote financial inclusion worldwide.</p>
                ''',
                'date': timezone.now().date(),
            },
        ]

        created_count = 0
        for i in range(min(count, len(sample_posts))):
            post_data = sample_posts[i]

            # Create unique slug
            base_slug = f'sample-post-{i+1}'
            slug = base_slug
            counter = 1
            while Page.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1

            # Create the blog post
            blog_post = ArticlePage(
                title=post_data['title'],
                slug=slug,
                date=post_data['date'],
                intro=post_data['intro'],
                body=post_data['body'],
                live=True,  # Make it live immediately
            )

            # Add it as a child of the news index page
            news_index.add_child(instance=blog_post)

            # Add categories
            blog_post.article_types.add(news_type)
            blog_post.locations.add(global_location)
            blog_post.sectors.add(freedom_sector)

            self.stdout.write(
                self.style.SUCCESS(f'Created blog post: "{blog_post.title}" (slug: {blog_post.slug})')
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample blog posts!')
        )
        self.stdout.write(
            'You can view them at: http://127.0.0.1:8000/news/'
        )