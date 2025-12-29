"""
Management command to scrape and import digital assets from the old CashMatters website.

Usage:
    python manage.py import_assets                    # Scrape all assets
    python manage.py import_assets --dry-run          # Preview without downloading
    python manage.py import_assets --category=logos   # Import specific category
"""

import os
import re
import json
import tempfile
import hashlib
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote, parse_qs

import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    from wagtail.images.models import Image
    from taggit.models import Tag
    WAGTAIL_AVAILABLE = True
except ImportError:
    WAGTAIL_AVAILABLE = False


class CMSClient:
    """Access the old CashMatters CMS API with authentication."""

    CMS_BASE = "https://cashmatters.backend-api.io"

    def __init__(self, stdout, style, username=None, password=None):
        self.stdout = stdout
        self.style = style
        self.session = requests.Session()
        self.authenticated = False

        if username and password:
            self.authenticate(username, password)

    def authenticate(self, username, password):
        """Authenticate with the CMS."""
        try:
            # Try to login
            login_url = f"{self.CMS_BASE}/cms/login/"

            # Get CSRF token first
            response = self.session.get(login_url, timeout=30)

            # Extract CSRF token from cookies or form
            csrf_token = self.session.cookies.get('csrftoken', '')

            # Post login credentials
            login_data = {
                'username': username,
                'password': password,
                'csrfmiddlewaretoken': csrf_token,
            }

            response = self.session.post(
                login_url,
                data=login_data,
                headers={'Referer': login_url},
                timeout=30
            )

            if response.status_code == 200 and 'login' not in response.url.lower():
                self.authenticated = True
                self.stdout.write(self.style.SUCCESS("  Authenticated with CMS"))
            else:
                self.stdout.write(self.style.WARNING("  CMS authentication failed"))

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  CMS auth error: {e}"))

    def get_images(self):
        """Fetch all images from the CMS API."""
        if not self.authenticated:
            return []

        images = []
        try:
            # Try Wagtail API v2
            api_url = f"{self.CMS_BASE}/api/v2/images/"
            response = self.session.get(api_url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    if 'meta' in item and 'download_url' in item['meta']:
                        images.append(item['meta']['download_url'])
                    elif 'file' in item:
                        images.append(f"{self.CMS_BASE}{item['file']}")

                self.stdout.write(f"  Found {len(images)} images in CMS")

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  Error fetching CMS images: {e}"))

        return images


class AssetScraper:
    """Scrape assets from cashmatters.org and its CDN."""

    CDN_BASE = "https://d3an988loexeh7.cloudfront.net"
    SITE_URL = "https://www.cashmatters.org"

    PAGES_TO_SCRAPE = [
        "/",
        "/supporter-resources",
        "/why-cash-matters",
        "/about",
        "/key-facts",
        "/blog",
        "/blog?types=key-facts",
        "/blog?types=news",
    ]

    # Known asset patterns on CDN - enumerate these
    KNOWN_CDN_ASSETS = [
        # Fact cards (key-fact pattern)
        "https://d3an988loexeh7.cloudfront.net/media/media/images/key-fact-2120_g0hl7Ko.png",
        "https://d3an988loexeh7.cloudfront.net/media/media/images/key-fact-2121_lbCK4fP.png",
        # Logos
        "https://d3an988loexeh7.cloudfront.net/media/original_images/cash-matters-logo-white.png",
        "https://d3an988loexeh7.cloudfront.net/media/original_images/cash-matters-logo-black.png",
        "https://d3an988loexeh7.cloudfront.net/media/original_images/cash-matters-logo.png",
        # Banners
        "https://d3an988loexeh7.cloudfront.net/media/original_images/assets-header.png",
        "https://d3an988loexeh7.cloudfront.net/media/original_images/we-support-cash-banner.png",
        # World/regional images
        "https://d3an988loexeh7.cloudfront.net/media/images/world-global-1140x750.width-1660.jpegquality-80.jpg",
    ]

    # Known Vimeo video IDs
    KNOWN_VIDEOS = [
        {"id": "488891865", "title": "Freedom Matters"},
        {"id": "417517809", "title": "Choice Matters"},
        {"id": "417517552", "title": "Cash Matters"},
    ]

    def __init__(self, stdout, style):
        self.stdout = stdout
        self.style = style
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def scrape_all_assets(self):
        """Scrape all pages and collect asset URLs."""
        assets = {
            'images': set(),
            'videos': list(self.KNOWN_VIDEOS),
        }

        # Add known CDN assets first
        self.stdout.write("Adding known CDN assets...")
        for url in self.KNOWN_CDN_ASSETS:
            assets['images'].add(url)

        # Also try to enumerate key-fact patterns (key-fact-XXXX)
        self.stdout.write("Enumerating key-fact patterns...")
        for i in range(2100, 2150):  # Try a range of IDs
            for suffix in ['', '_g0hl7Ko', '_lbCK4fP', '_abc123']:
                url = f"https://d3an988loexeh7.cloudfront.net/media/media/images/key-fact-{i}{suffix}.png"
                # We'll validate these later during download
                assets['images'].add(url)

        for page_path in self.PAGES_TO_SCRAPE:
            url = urljoin(self.SITE_URL, page_path)
            self.stdout.write(f"Scraping: {url}")

            try:
                page_assets = self.scrape_page(url)
                assets['images'].update(page_assets['images'])

                # Add new videos if found
                for video in page_assets['videos']:
                    if video not in [v['id'] for v in assets['videos']]:
                        assets['videos'].append({"id": video, "title": f"Video {video}"})

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Error scraping {url}: {e}"))

        # Clean up URLs - extract real CDN URLs from Next.js proxy URLs
        cleaned_images = set()
        for url in assets['images']:
            cleaned = self._clean_url(url)
            if cleaned:
                cleaned_images.add(cleaned)

        assets['images'] = list(cleaned_images)
        return assets

    def _clean_url(self, url):
        """Extract real CDN URL from Next.js image proxy or clean raw URL."""
        # Handle Next.js /_next/image proxy URLs
        if '/_next/image' in url:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            if 'url' in query_params:
                real_url = unquote(query_params['url'][0])
                return self._clean_url(real_url)  # Recurse to clean the extracted URL
            return None

        # Direct CDN URL - clean it up
        if 'd3an988loexeh7.cloudfront.net' in url:
            # Remove HTML entities and garbage
            url = url.split('&#')[0]  # Remove HTML entities
            url = url.split("'")[0]   # Remove trailing quotes
            url = url.split('"')[0]   # Remove double quotes

            # Ensure URL ends with valid image extension
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.avif']
            has_valid_ext = any(ext in url.lower() for ext in valid_extensions)
            if not has_valid_ext:
                return None

            return url

        return None

    def scrape_page(self, url):
        """Scrape a single page for CDN asset URLs."""
        assets = {
            'images': set(),
            'videos': [],
        }

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            self.stdout.write(self.style.WARNING(f"  Failed to fetch {url}: {e}"))
            return assets

        html = response.text

        # Find all CDN image URLs using regex
        cdn_pattern = r'https?://d3an988loexeh7\.cloudfront\.net/media/[^\s\"\'\)>]+'
        cdn_urls = re.findall(cdn_pattern, html)

        for url in cdn_urls:
            # Clean up URL (remove trailing quotes, etc.)
            url = url.rstrip('\"\')')
            if self._is_image_url(url):
                assets['images'].add(url)

        # Find Vimeo video IDs
        vimeo_pattern = r'vimeo\.com/(?:video/)?(\d+)'
        vimeo_ids = re.findall(vimeo_pattern, html)
        assets['videos'].extend(set(vimeo_ids))

        # Also parse with BeautifulSoup if available
        if BS4_AVAILABLE:
            soup = BeautifulSoup(html, 'html.parser')

            # Find img tags
            for img in soup.find_all('img'):
                src = img.get('src', '') or img.get('data-src', '')
                if 'd3an988loexeh7.cloudfront.net' in src:
                    assets['images'].add(src)

            # Find background images in style attributes
            for elem in soup.find_all(style=True):
                style = elem['style']
                urls = re.findall(r'url\([\'"]?([^\'"\)]+)[\'"]?\)', style)
                for url in urls:
                    if 'd3an988loexeh7.cloudfront.net' in url:
                        assets['images'].add(url)

        self.stdout.write(f"  Found {len(assets['images'])} images, {len(assets['videos'])} videos")
        return assets

    def _is_image_url(self, url):
        """Check if URL points to an image."""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.avif']
        parsed = urlparse(url)
        path_lower = parsed.path.lower()
        return any(ext in path_lower for ext in image_extensions)


class AssetDownloader:
    """Download assets from URLs."""

    def __init__(self, stdout, style, skip_failed=True):
        self.stdout = stdout
        self.style = style
        self.skip_failed = skip_failed
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def download(self, url, max_retries=2):
        """Download a file from URL with retries."""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)

                # Skip 404s silently
                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.content

            except requests.RequestException as e:
                if '404' in str(e) or 'Not Found' in str(e):
                    return None  # Skip 404s silently
                if attempt < max_retries - 1:
                    continue  # Retry silently
                if not self.skip_failed:
                    raise e
        return None

    def categorize_asset(self, filename, url):
        """Determine category based on filename patterns."""
        filename_lower = filename.lower()
        url_lower = url.lower()

        if 'logo' in filename_lower or 'logo' in url_lower:
            return 'logos'
        elif 'banner' in filename_lower or 'header' in filename_lower:
            return 'banners'
        elif 'fact' in filename_lower:
            return 'fact-cards'
        elif 'post' in filename_lower or 'card' in filename_lower:
            return 'post-cards'
        else:
            return 'general'

    def get_filename_from_url(self, url):
        """Extract clean filename from URL."""
        parsed = urlparse(url)
        path = parsed.path
        filename = os.path.basename(path)
        # Remove Wagtail rendition suffixes like .2e16d0ba.fill-343x225
        filename = re.sub(r'\.[a-f0-9]{8}\.[\w-]+(?=\.\w+$)', '', filename)
        return filename


class WagtailUploader:
    """Upload images to Wagtail's image library."""

    def __init__(self, stdout, style):
        self.stdout = stdout
        self.style = style

    def upload_image(self, content, filename, category):
        """Upload image content to Wagtail Image library."""
        if not WAGTAIL_AVAILABLE:
            self.stdout.write(self.style.ERROR("Wagtail not available"))
            return None

        # Check if image already exists
        existing = Image.objects.filter(title=filename).first()
        if existing:
            self.stdout.write(f"  Image already exists: {filename}")
            return existing

        try:
            # Create image file
            image_file = ContentFile(content, name=filename)

            # Create Wagtail image
            image = Image(
                title=filename,
                file=image_file,
            )
            image.save()

            # Add category tag
            image.tags.add(f"support-{category}")
            image.tags.add("imported")

            self.stdout.write(self.style.SUCCESS(f"  Uploaded: {filename}"))
            return image

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Failed to upload {filename}: {e}"))
            return None


class Command(BaseCommand):
    help = 'Import digital assets from the old CashMatters website'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            choices=['scrape', 'cms', 'both'],
            default='scrape',
            help='Source to import from (default: scrape)',
        )
        parser.add_argument(
            '--category',
            choices=['logos', 'banners', 'fact-cards', 'post-cards', 'videos', 'all'],
            default='all',
            help='Category to import (default: all)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be downloaded without downloading',
        )
        parser.add_argument(
            '--output-dir',
            default='cashmatters/static/images/support/',
            help='Output directory for static files',
        )
        parser.add_argument(
            '--update-template',
            action='store_true',
            default=True,
            help='Update support.html template with new assets',
        )
        parser.add_argument(
            '--cms-user',
            default='directorgeneral',
            help='CMS username for authentication',
        )
        parser.add_argument(
            '--cms-pass',
            default='SYz6fZ8ndjkf3v',
            help='CMS password for authentication',
        )
        parser.add_argument(
            '--skip-failed',
            action='store_true',
            default=True,
            help='Skip URLs that return 404 (default: True)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== CashMatters Asset Importer ===\n'))

        if not BS4_AVAILABLE:
            self.stdout.write(self.style.WARNING(
                'BeautifulSoup4 not installed. Run: pip install beautifulsoup4\n'
                'Continuing with regex-only scraping...\n'
            ))

        # Initialize components
        scraper = AssetScraper(self.stdout, self.style)
        downloader = AssetDownloader(self.stdout, self.style, skip_failed=options['skip_failed'])
        uploader = WagtailUploader(self.stdout, self.style)

        assets = {
            'images': [],
            'videos': [],
        }

        # Step 1: Scrape assets based on source
        source = options['source']

        if source in ['scrape', 'both']:
            self.stdout.write('\n[1/4] Scraping cashmatters.org for assets...\n')
            scraped = scraper.scrape_all_assets()
            assets['images'].extend(scraped['images'])
            assets['videos'].extend(scraped['videos'])

        if source in ['cms', 'both']:
            self.stdout.write('\n[1/4] Fetching assets from CMS API...\n')
            cms = CMSClient(
                self.stdout,
                self.style,
                username=options['cms_user'],
                password=options['cms_pass']
            )
            cms_images = cms.get_images()
            assets['images'].extend(cms_images)

        # Deduplicate
        assets['images'] = list(set(assets['images']))
        assets['videos'] = list({v['id']: v for v in assets['videos']}.values())

        self.stdout.write(self.style.SUCCESS(
            f'\nFound {len(assets["images"])} images and {len(assets["videos"])} videos\n'
        ))

        if options['dry_run']:
            self._show_dry_run_results(assets)
            return

        # Step 2: Create output directory
        output_dir = Path(settings.BASE_DIR) / options['output_dir']
        self.stdout.write(f'\n[2/4] Creating directory structure at {output_dir}...\n')
        self._create_directories(output_dir)

        # Step 3: Download and upload images
        self.stdout.write('\n[3/4] Downloading and uploading images...\n')
        uploaded_assets = self._process_images(
            assets['images'],
            downloader,
            uploader,
            output_dir,
            options['category']
        )

        # Step 4: Save video metadata
        self._save_video_metadata(assets['videos'], output_dir)

        # Step 5: Update template if requested
        if options['update_template']:
            self.stdout.write('\n[4/4] Updating support.html template...\n')
            self._update_template(uploaded_assets, assets['videos'])

        self.stdout.write(self.style.SUCCESS('\n=== Import Complete ===\n'))

    def _show_dry_run_results(self, assets):
        """Display what would be downloaded in dry-run mode."""
        self.stdout.write('\n--- DRY RUN: Would download these assets ---\n')

        self.stdout.write('\nImages:')
        for url in sorted(assets['images'])[:20]:
            self.stdout.write(f'  - {url}')
        if len(assets['images']) > 20:
            self.stdout.write(f'  ... and {len(assets["images"]) - 20} more')

        self.stdout.write('\nVideos:')
        for video in assets['videos']:
            self.stdout.write(f'  - Vimeo ID: {video["id"]} ({video["title"]})')

        self.stdout.write('\n--- End of dry run ---\n')

    def _create_directories(self, output_dir):
        """Create the directory structure for assets."""
        categories = ['logos', 'banners', 'fact-cards', 'post-cards', 'general']
        for category in categories:
            cat_dir = output_dir / category
            cat_dir.mkdir(parents=True, exist_ok=True)
            self.stdout.write(f'  Created: {cat_dir}')

    def _process_images(self, image_urls, downloader, uploader, output_dir, category_filter):
        """Download and upload all images."""
        uploaded = {
            'logos': [],
            'banners': [],
            'fact-cards': [],
            'post-cards': [],
            'general': [],
        }

        success_count = 0
        skip_count = 0

        for url in image_urls:
            filename = downloader.get_filename_from_url(url)
            category = downloader.categorize_asset(filename, url)

            # Apply category filter
            if category_filter != 'all' and category != category_filter:
                continue

            try:
                # Download the file
                content = downloader.download(url)
                if not content:
                    skip_count += 1
                    continue

                self.stdout.write(f'Downloaded: {filename}')

                # Save to static directory
                save_path = output_dir / category / filename
                with open(save_path, 'wb') as f:
                    f.write(content)

                # Upload to Wagtail
                if WAGTAIL_AVAILABLE:
                    image = uploader.upload_image(content, filename, category)
                    if image:
                        uploaded[category].append({
                            'filename': filename,
                            'wagtail_id': image.id,
                            'url': url,
                        })
                        success_count += 1
                else:
                    uploaded[category].append({
                        'filename': filename,
                        'static_path': str(save_path),
                        'url': url,
                    })
                    success_count += 1

            except Exception as e:
                skip_count += 1

        self.stdout.write(f'\nProcessed: {success_count} downloaded, {skip_count} skipped (404 or failed)')
        return uploaded

    def _save_video_metadata(self, videos, output_dir):
        """Save video metadata to JSON file."""
        video_file = output_dir / 'videos.json'
        with open(video_file, 'w') as f:
            json.dump(videos, f, indent=2)
        self.stdout.write(f'\nSaved video metadata to: {video_file}')

    def _update_template(self, uploaded_assets, videos):
        """Update the support.html template with actual assets."""
        template_path = Path(settings.BASE_DIR) / 'cashmatters/templates/support.html'

        if not template_path.exists():
            self.stdout.write(self.style.ERROR(f'Template not found: {template_path}'))
            return

        with open(template_path, 'r') as f:
            content = f.read()

        # Update Videos tab
        video_html = self._generate_videos_html(videos)
        content = re.sub(
            r'(<div class="tab-pane fade" id="videos-content"[^>]*>)\s*<div class="text-center py-5 text-muted">Videos Content Coming Soon\.\.\.</div>',
            r'\1\n' + video_html,
            content
        )

        # Update Fact Cards tab
        if uploaded_assets.get('fact-cards'):
            fact_cards_html = self._generate_cards_html(uploaded_assets['fact-cards'], 'fact-card')
            content = re.sub(
                r'(<div class="tab-pane fade" id="facts-content"[^>]*>)\s*<div class="text-center py-5 text-muted">Fact Cards Content Coming Soon\.\.\.</div>',
                r'\1\n' + fact_cards_html,
                content
            )

        # Update Post Cards tab
        if uploaded_assets.get('post-cards'):
            post_cards_html = self._generate_cards_html(uploaded_assets['post-cards'], 'post-card')
            content = re.sub(
                r'(<div class="tab-pane fade" id="post-content"[^>]*>)\s*<div class="text-center py-5 text-muted">Post Cards Content Coming Soon\.\.\.</div>',
                r'\1\n' + post_cards_html,
                content
            )

        with open(template_path, 'w') as f:
            f.write(content)

        self.stdout.write(self.style.SUCCESS(f'Updated template: {template_path}'))

    def _generate_videos_html(self, videos):
        """Generate HTML for video embeds."""
        html = '                    <div class="row g-4">\n'
        for video in videos:
            html += f'''                        <div class="col-lg-4 col-md-6">
                            <div class="ratio ratio-16x9 mb-2">
                                <iframe src="https://player.vimeo.com/video/{video["id"]}"
                                        frameborder="0"
                                        allow="autoplay; fullscreen; picture-in-picture"
                                        allowfullscreen>
                                </iframe>
                            </div>
                            <p class="text-center text-muted small">{video["title"]}</p>
                        </div>
'''
        html += '                    </div>'
        return html

    def _generate_cards_html(self, assets, card_type):
        """Generate HTML for card grids."""
        html = '                    <div class="row g-4">\n'
        for asset in assets:
            filename = asset['filename']
            category = 'fact-cards' if card_type == 'fact-card' else 'post-cards'
            html += f'''                        <div class="col-lg-4 col-md-6">
                            <div class="asset-card bg-white d-flex align-items-center justify-content-center p-3 mb-2">
                                <img src="{{% static 'images/support/{category}/{filename}' %}}" alt="{filename}" class="img-fluid">
                            </div>
                            <div class="d-flex justify-content-end gap-3 small text-muted px-2">
                                <a href="{{% static 'images/support/{category}/{filename}' %}}" download="{filename}" class="text-reset text-decoration-none hover-mint"><i class="bi bi-download"></i> Download</a>
                                <a href="#" class="text-reset text-decoration-none hover-mint"><i class="bi bi-facebook"></i> Share</a>
                            </div>
                        </div>
'''
        html += '                    </div>'
        return html
