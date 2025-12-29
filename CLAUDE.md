# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CashMatters is a Wagtail-based CMS for content publishing with blog/vlog functionality, news publishing, and a custom dashboard. Built on Django 4.2.7 and Wagtail 5.2.5.

## Development Commands

```bash
# Start development server
python manage.py runserver

# Database operations
python manage.py migrate                    # Apply migrations
python manage.py makemigrations             # Create migrations
python manage.py createsuperuser            # Create admin user

# Static files (production)
python manage.py collectstatic --noinput

# Custom management commands
python manage.py populate_categories        # Populate ArticleType, Location, Sector
python manage.py create_sample_posts        # Create sample blog posts
python manage.py create_essential_pages     # Create required page structure
```

## Environment Configuration

Split settings in `cashmatters/settings/`:
- `dev.py` - Development (DEBUG=True, SQLite)
- `production.py` - Production (DEBUG=False, PostgreSQL, SSL)
- `base.py` - Shared configuration

Set via `DJANGO_SETTINGS_MODULE` (defaults to `cashmatters.settings.dev` in manage.py).

## Architecture

### Django Apps
- `blog/` - Core content management (BlogPage, ArticlePage, categorization snippets)
- `home/` - HomePage model
- `search/` - Search functionality

### Key Models (blog/models.py)
- **BlogPage/ArticlePage** - Content pages with StreamField body, thumbnails, featured flag, categorization via M2M to ArticleType/Location/Sector snippets
- **BlogIndexPage/NewsIndexPage** - Parent listing pages for blogs and news/articles
- **SupportPage/WhyCashMattersPage** - Singleton pages (enforced via `clean()` method validation + wagtail_hooks.py redirect)
- **KeyFactsPage** - Child of NewsIndexPage for key facts content
- **ArticleType/Location/Sector** - Categorization snippet models

### Content System
StreamField blocks defined in models: heading, paragraph, image, quote (QuoteBlock), embed, document.

Custom blocks:
- `QuoteBlock` - Structured quote with name, job_title, company fields
- `FactBlock` - For WhyCashMattersPage facts with reveal functionality
- `FeatureCardBlock` - Icon cards with content sections

### Custom Admin Extensions (blog/wagtail_hooks.py)
- Custom menu items: Blogs Dashboard, Support Cash Page, Why Cash Matters Page
- After-create/edit redirects for BlogPage → `/admin/all-blogs/`
- Singleton enforcement for WhyCashMattersPage and SupportPage (redirects to edit existing)

### URL Structure
Frontend views defined inline in `cashmatters/urls.py`:
- `/` - Homepage (`index` view) - latest 3 posts + featured posts
- `/news/` - Paginated news with search/category filtering, AJAX infinite scroll
- `/support/` - Support page (fetches SupportPage singleton)
- `/why-cash/` - Why Cash Matters page (fetches WhyCashMattersPage with slug='why-cash')
- `/about/` - Static about page
- `/author/<author_name>/` - Author profile with all posts by author
- `/admin/all-blogs/` - Custom blogs dashboard (staff only, bulk publish/unpublish/delete)
- `/admin/` - Wagtail admin
- `/api/v2/` - Wagtail API v2

### Templates
- Global: `cashmatters/templates/` (index.html, news.html, blog-details.html, support.html, why-cash.html, author.html, blogs_dashboard.html)
- Blog: `blog/templates/blog/` (blog-details.html is shared template for BlogPage and ArticlePage)
- Custom admin login: `cashmatters/templates/wagtailadmin/login.html`

### Static Files
- Development source: `cashmatters/static/` (css/, js/, images/, videos/)
- Production collected: `staticfiles/`
- User uploads: `media/`

## API

Wagtail API v2 at `/api/v2/` with custom BlogPagesAPIViewSet in `blog/api.py`.

## Deployment

Docker + Nginx + Gunicorn stack:
- `docker-compose.yml` - Two services (Django + Nginx)
- `nginx.conf` - Reverse proxy with static caching
- `gunicorn.service` - Systemd service (3 workers, Unix socket)
- `deploy-server.sh` / `post-deploy.sh` - Deployment scripts

## Database

- Development: SQLite (`db.sqlite3`)
- Production: PostgreSQL via Neon cloud (configured in base.py)
