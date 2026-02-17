from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import activate
import os

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views
from blog.api import api_router





# Frontend views
def index(request):
    """Serve the homepage with latest blog posts and dynamic hero carousel"""
    from blog.models import ArticlePage, BlogPage, ArticleType, KeyFactsPage
    from itertools import chain

    # Posts to hide from homepage (by title)
    hidden_titles = [
        "95% of physical payment locations accept cash throughout the euro area",
    ]

    # Track all used post IDs to prevent duplicates across sections
    used_post_ids = set()

    # =========================================
    # 1. HERO POSTS - Get one post from each category (highest priority)
    # =========================================
    all_categories = ArticleType.objects.all()

    hero_posts_by_category = []

    for category in all_categories:
        # Try to get an ArticlePage with this category first
        article = ArticlePage.objects.live().select_related(
            'author_profile'
        ).prefetch_related('article_types').filter(
            article_types=category
        ).exclude(id__in=used_post_ids).exclude(title__in=hidden_titles).order_by('-featured', '-date').first()

        if article:
            hero_posts_by_category.append(article)
            used_post_ids.add(article.id)
            continue

        # If no ArticlePage, try BlogPage
        blog_post = BlogPage.objects.live().select_related(
            'author_profile'
        ).prefetch_related('article_types').filter(
            article_types=category
        ).exclude(id__in=used_post_ids).exclude(title__in=hidden_titles).order_by('-featured', '-date').first()

        if blog_post:
            hero_posts_by_category.append(blog_post)
            used_post_ids.add(blog_post.id)

    # If we have less than 3 posts from categories, fill with latest posts
    if len(hero_posts_by_category) < 3:
        additional_articles = ArticlePage.objects.live().select_related(
            'author_profile'
        ).prefetch_related('article_types').exclude(
            id__in=used_post_ids
        ).exclude(title__in=hidden_titles).order_by('-featured', '-date')[:5]

        additional_blogs = BlogPage.objects.live().select_related(
            'author_profile'
        ).prefetch_related('article_types').exclude(
            id__in=used_post_ids
        ).exclude(title__in=hidden_titles).order_by('-featured', '-date')[:5]

        additional_combined = sorted(
            chain(additional_articles, additional_blogs),
            key=lambda x: x.date,
            reverse=True
        )

        for post in additional_combined:
            if len(hero_posts_by_category) >= 5:
                break
            hero_posts_by_category.append(post)
            used_post_ids.add(post.id)

    # Sort hero posts by date (newest first) for better carousel order
    hero_posts_combined = sorted(
        hero_posts_by_category,
        key=lambda x: x.date,
        reverse=True
    )[:8]  # Max 8 slides for variety across all categories

    # =========================================
    # 2. FEATURED POSTS - Exclude posts already in hero
    # =========================================
    featured_articles = ArticlePage.objects.live().select_related(
        'author_profile'
    ).filter(featured=True).exclude(id__in=used_post_ids).exclude(title__in=hidden_titles).order_by('-date')[:5]

    featured_blog_posts = BlogPage.objects.live().select_related(
        'author_profile'
    ).filter(featured=True).exclude(id__in=used_post_ids).exclude(title__in=hidden_titles).order_by('-date')[:5]

    # Combine featured posts
    featured_posts = sorted(
        chain(featured_articles, featured_blog_posts),
        key=lambda x: x.date,
        reverse=True
    )[:3]  # Take only the 3 most recent featured posts

    # Add featured post IDs to used set
    for post in featured_posts:
        used_post_ids.add(post.id)

    # =========================================
    # 3. LATEST POSTS - Exclude posts already in hero AND featured
    # =========================================
    latest_articles = ArticlePage.objects.live().select_related(
        'author_profile'
    ).exclude(id__in=used_post_ids).exclude(title__in=hidden_titles).order_by('-date')[:5]

    latest_blog_posts = BlogPage.objects.live().select_related(
        'author_profile'
    ).exclude(id__in=used_post_ids).exclude(title__in=hidden_titles).order_by('-date')[:5]

    # Combine and sort by date (newest first)
    latest_posts = sorted(
        chain(latest_articles, latest_blog_posts),
        key=lambda x: x.date,
        reverse=True
    )[:3]  # Take only the 3 most recent

    # =========================================
    # 4. PODCAST POSTS - Get latest podcast episodes
    # =========================================
    podcast_articles = ArticlePage.objects.live().select_related(
        'author_profile'
    ).prefetch_related('article_types').filter(
        article_types__name__in=['Podcast', 'Podcasts', 'Audio']
    ).order_by('-date')[:3]

    podcast_blog_posts = BlogPage.objects.live().select_related(
        'author_profile'
    ).prefetch_related('article_types').filter(
        article_types__name__in=['Podcast', 'Podcasts', 'Audio']
    ).order_by('-date')[:3]

    # Combine and sort podcast posts by date
    podcast_posts = sorted(
        chain(podcast_articles, podcast_blog_posts),
        key=lambda x: x.date,
        reverse=True
    )[:3]  # Take only the 3 most recent podcasts

    # =========================================
    # 5. STUDIES & REPORTS POSTS
    # =========================================
    studies_articles = ArticlePage.objects.live().select_related(
        'author_profile'
    ).prefetch_related('article_types').filter(
        article_types__name__in=['Studies', 'Research', 'Studies & Research']
    ).order_by('-date')[:2]

    studies_blog_posts = BlogPage.objects.live().select_related(
        'author_profile'
    ).prefetch_related('article_types').filter(
        article_types__name__in=['Studies', 'Research', 'Studies & Research']
    ).order_by('-date')[:2]

    # Combine and sort studies posts by date
    studies_posts = sorted(
        chain(studies_articles, studies_blog_posts),
        key=lambda x: x.date,
        reverse=True
    )[:2]  # Take only the 2 most recent studies/reports

    # =========================================
    # 6. KEY FACTS - Dynamic from KeyFactsPage
    # =========================================
    key_facts = KeyFactsPage.objects.live().order_by('-date')[:4]

    context = {
        'latest_posts': latest_posts,
        'featured_posts': featured_posts,
        'hero_posts': hero_posts_combined,
        'podcast_posts': podcast_posts,
        'studies_posts': studies_posts,
        'key_facts': key_facts,
    }
    return render(request, 'index.html', context)


def news(request):
    """Serve the news page with dynamic articles and blog posts"""
    from blog.models import ArticlePage, BlogPage
    from itertools import chain
    from django.core.paginator import Paginator
    from django.http import JsonResponse
    from django.template.loader import render_to_string
    from django.db.models import Q
    from datetime import datetime

    # Get search query and filters
    search_query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    # Get all published articles and blog posts with author_profile preloaded
    articles = ArticlePage.objects.live().select_related('author_profile').order_by('-date')
    blog_posts = BlogPage.objects.live().select_related('author_profile').order_by('-date')

    # Apply category filter if specified
    if category:
        # Map category names to article type names (updated mapping)
        category_mapping = {
            'news': ['News'],
            'studies': ['Studies', 'Research', 'Studies & Research'],
            'key-facts': ['Key Facts'],
            'podcast': ['Podcast', 'Podcasts', 'Audio'],
            'events': ['Events'],
        }

        article_type_names = category_mapping.get(category.lower(), [])
        if article_type_names:
            articles = articles.filter(article_types__name__in=article_type_names)
            blog_posts = blog_posts.filter(article_types__name__in=article_type_names)

    # Apply date range filter
    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
            articles = articles.filter(date__gte=date_from_parsed)
            blog_posts = blog_posts.filter(date__gte=date_from_parsed)
        except ValueError:
            pass  # Invalid date format, skip filter

    if date_to:
        try:
            date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
            articles = articles.filter(date__lte=date_to_parsed)
            blog_posts = blog_posts.filter(date__lte=date_to_parsed)
        except ValueError:
            pass  # Invalid date format, skip filter

    # Apply search filter if query exists
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(intro__icontains=search_query)
        )
        blog_posts = blog_posts.filter(
            Q(title__icontains=search_query) |
            Q(intro__icontains=search_query)
        )

    # Combine and sort by date (newest first)
    combined_posts = sorted(
        chain(articles, blog_posts),
        key=lambda x: x.date,
        reverse=True
    )

    # Pagination - 6 posts per page
    paginator = Paginator(combined_posts, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return just the article HTML for AJAX requests
        article_html = render_to_string('news_articles.html', {
            'articles': page_obj,
            'has_next': page_obj.has_next(),
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        })
        return JsonResponse({
            'html': article_html,
            'has_next': page_obj.has_next(),
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        })

    # Debug: Print posts and dates
    print(f"DEBUG: Total articles: {articles.count()}")
    print(f"DEBUG: Total blog posts: {blog_posts.count()}")
    print(f"DEBUG: Total combined posts: {len(combined_posts)}")
    print(f"DEBUG: Page {page_number} has {len(page_obj)} posts")
    if search_query:
        print(f"DEBUG: Search query: '{search_query}'")
    if category:
        print(f"DEBUG: Category filter: '{category}'")
    if content_type:
        print(f"DEBUG: Content type filter: '{content_type}'")
    if date_from or date_to:
        print(f"DEBUG: Date range: {date_from} to {date_to}")

    context = {
        'articles': page_obj,  # Now this is a page object, not the full list
        'has_next': page_obj.has_next(),
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'search_query': search_query,
        'active_category': category,
    }
    return render(request, 'news.html', context)


def author(request, author_name=None, author_id=None):
    """Serve the author profile page showing all articles by a specific author"""
    from blog.models import ArticlePage, BlogPage, Author
    from itertools import chain
    from django.shortcuts import get_object_or_404
    from django.http import Http404

    author_obj = None
    articles = []
    blog_posts = []

    # Try to get author by ID first (preferred method)
    if author_id:
        author_obj = get_object_or_404(Author, id=author_id)
        # Get posts by author_profile with optimized queries
        articles = list(ArticlePage.objects.live().filter(author_profile=author_obj).only(
            'title', 'date', 'url_path', 'slug'
        ).prefetch_related('article_types').order_by('-date')[:50])
        blog_posts = list(BlogPage.objects.live().filter(author_profile=author_obj).only(
            'title', 'date', 'url_path', 'slug'
        ).prefetch_related('article_types').order_by('-date')[:50])
    elif author_name:
        # Try to find author by name (new Author model)
        author_obj = Author.objects.filter(name__iexact=author_name).first()

        if author_obj:
            # Get posts by author_profile with optimized queries
            articles = list(ArticlePage.objects.live().filter(author_profile=author_obj).only(
                'title', 'date', 'url_path', 'slug'
            ).prefetch_related('article_types').order_by('-date')[:50])
            blog_posts = list(BlogPage.objects.live().filter(author_profile=author_obj).only(
                'title', 'date', 'url_path', 'slug'
            ).prefetch_related('article_types').order_by('-date')[:50])
        else:
            # Fall back to legacy CharField author field
            articles = list(ArticlePage.objects.live().filter(author__iexact=author_name).only(
                'title', 'date', 'url_path', 'slug'
            ).prefetch_related('article_types').order_by('-date')[:50])
            blog_posts = list(BlogPage.objects.live().filter(author__iexact=author_name).only(
                'title', 'date', 'url_path', 'slug'
            ).prefetch_related('article_types').order_by('-date')[:50])
    else:
        raise Http404("Author not found")

    # Combine and sort by date (newest first) - limit to 50 total
    author_posts = sorted(
        chain(articles, blog_posts),
        key=lambda x: x.date,
        reverse=True
    )[:50]

    context = {
        'author': author_obj,
        'author_name': author_obj.name if author_obj else author_name,
        'articles': author_posts,
        'total_articles': len(author_posts),
    }
    return render(request, 'author.html', context)


def support(request):
    """Serve the support page with dynamic content"""
    from blog.models import SupportPage

    # Get the SupportPage content
    page = SupportPage.objects.live().first()

    context = {
        'page': page,
    }

    return render(request, 'support.html', context)


def blogs_dashboard_redirect(request):
    """Redirect old blogs URL to new admin location"""
    return redirect('/admin/all-blogs/')


def about(request):
    """Serve the about page"""
    return render(request, 'about.html')


def privacy(request):
    """Serve the privacy policy page"""
    return render(request, 'privacy.html')


def write_for_us(request):
    """Serve the Write for Us page"""
    return render(request, 'write_for_us.html')


def why_cash(request):
    """Serve the Why Cash Matters page"""
    return render(request, 'why-cash.html')


def new_page(request):
    """Serve the Why Cash Matters Feature page - with Wagtail page fallback"""
    from blog.models import WhyCashMattersFeaturePage

    # Try to get the Wagtail page first (including drafts for preview)
    try:
        # First try to get published page, then any page
        page = (WhyCashMattersFeaturePage.objects.live().first() or
                WhyCashMattersFeaturePage.objects.first())
        if page:
            print(f"Found page: {page.title}, Cards: {len(page.feature_cards)}")
            # Use Wagtail's serve method to render the page
            return page.serve(request)
    except Exception as e:
        print(f"Error loading WhyCashMattersFeaturePage: {e}")
    # Fallback to static template if no Wagtail page exists
    print("Falling back to static template")
    return render(request, 'new_page.html')


def create_blog_page(request):
    """Redirect to Wagtail admin for creating blog posts with clean URL"""
    from blog.models import BlogIndexPage
    from django.http import HttpResponsePermanentRedirect
    from home.models import HomePage

    try:
        # Get the first BlogIndexPage
        # (assuming there's only one main blog index)
        blog_index = BlogIndexPage.objects.live().first()
        if blog_index:
            url = f'/admin/pages/add/blog/blogpage/{blog_index.id}/'
            return HttpResponsePermanentRedirect(url)
        else:
            # If no BlogIndexPage exists, create one first
            home_page = HomePage.objects.live().first()
            if home_page:
                blog_index = BlogIndexPage(
                    title='Blog',
                    slug='blog',
                    intro='Latest blog posts and articles'
                )
                home_page.add_child(instance=blog_index)
                blog_index.save_revision().publish()
                url = f'/admin/pages/add/blog/blogpage/{blog_index.id}/'
                return HttpResponsePermanentRedirect(url)
            else:
                # If no HomePage exists, redirect to general add page
                return HttpResponsePermanentRedirect(
                    '/admin/pages/add/blog/blogpage/')
    except Exception:
        # Fallback to general add page if there's any error
        return HttpResponsePermanentRedirect(
            '/admin/pages/add/blog/blogpage/')



from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from wagtail.models import Page
from blog.models import BlogIndexPage


# blog/views.py

from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import reverse
from django.utils.text import slugify

from blog.models import BlogPage, BlogIndexPage, ArticleType, Location


@staff_member_required
def blogs_dashboard(request):
    # Base queryset
    qs_all = (
        BlogPage.objects
        .live()
        .select_related("owner")
        .prefetch_related("article_types", "locations")
    )
    total_count = qs_all.count()

    # --- filters ---
    search_query = (request.GET.get("q") or "").strip()
    type_filter = (request.GET.get("type") or "").strip()
    location_filter = (request.GET.get("location") or "").strip()

    qs = qs_all

    if search_query:
        qs = qs.filter(title__icontains=search_query)

    # type filter (slug -> ArticleType)
    if type_filter:
        t = next(
            (x for x in ArticleType.objects.all() if slugify(x.name) == type_filter),
            None
        )
        if t:
            qs = qs.filter(article_types__name=t.name)

    # location filter (slug -> Location)
    if location_filter:
        loc = next(
            (x for x in Location.objects.all() if slugify(x.name) == location_filter),
            None
        )
        if loc:
            qs = qs.filter(locations__name=loc.name)

    # Important: distinct BEFORE sorting (because of M2M filters)
    qs = qs.distinct()

    # --- sorting ---
    sort = (request.GET.get("sort") or "modified").strip()
    direction = (request.GET.get("dir") or "desc").strip().lower()

    SORT_MAP = {
        "title": "title",
        "date": "date",  # Post Date
        "modified": "latest_revision_created_at",  # Last modified
        "featured": "featured",
    }
    field = SORT_MAP.get(sort, "latest_revision_created_at")
    prefix = "-" if direction == "desc" else ""

    if sort == "featured":
        # Featured sort: respect dir
        # desc -> featured first, asc -> non-featured first
        if direction == "asc":
            qs = qs.order_by("featured", "-latest_revision_created_at", "title")
        else:
            qs = qs.order_by("-featured", "-latest_revision_created_at", "title")
    else:
        # normal sorts + stable tie-breaker
        qs = qs.order_by(f"{prefix}{field}", "-latest_revision_created_at", "title")

    filtered_count = qs.count()

    # --- pagination ---
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    # sidebar lists (for template)
    article_types = [
        {"name": t.name, "slug": slugify(t.name)}
        for t in ArticleType.objects.all().order_by("name")
    ]
    locations = [
        {"name": l.name, "slug": slugify(l.name)}
        for l in Location.objects.all().order_by("name")
    ]

    # add_url (Add blog page button)
    parent = BlogIndexPage.objects.first()
    if parent:
        add_url = reverse(
            "wagtailadmin_pages:add",
            kwargs={
                "content_type_app_name": "blog",
                "content_type_model_name": "blogpage",
                "parent_page_id": parent.id,
            },
        )
    else:
        add_url = reverse("wagtailadmin_explore_root")

    context = {
        "page_obj": page_obj,
        "blog_posts": page_obj.object_list,
        "total_count": total_count,
        "filtered_count": filtered_count,
        "search_query": search_query,
        "type_filter": type_filter,
        "location_filter": location_filter,
        "article_types": article_types,
        "locations": locations,
        "add_url": add_url,
        "sort": sort,
        "dir": direction,
    }
    return render(request, "blogs_dashboard.html", context)





# Language switch view
def set_language(request):
    """Handle language switching via GET parameter"""
    from django.utils import translation
    from django.conf import settings
    from django.http import HttpResponseRedirect

    # Django 4.0+ removed translation.LANGUAGE_SESSION_KEY
    # The session key for language is '_language'
    LANGUAGE_SESSION_KEY = '_language'

    lang = request.GET.get('lang', 'en-gb')
    if lang in [code for code, name in settings.LANGUAGES]:
        translation.activate(lang)
        request.session[LANGUAGE_SESSION_KEY] = lang

    # Redirect back to the referring page or home
    next_url = request.META.get('HTTP_REFERER', '/')
    # Remove any existing lang parameter from the URL
    if '?lang=' in next_url:
        next_url = next_url.split('?lang=')[0]
    elif '&lang=' in next_url:
        next_url = next_url.replace(f'&lang={lang}', '')

    # Create response with language cookie for persistence
    response = HttpResponseRedirect(next_url)
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,  # 'django_language'
        lang,
        max_age=365 * 24 * 60 * 60,  # 1 year
        path='/',
        samesite='Lax',
    )
    return response

from blog import admin_views
urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("set-language/", set_language, name="set_language"),

    path("", index, name="index"),
    path("news/", news, name="news"),
    path("about/", about, name="about"),
    path("privacy/", privacy, name="privacy"),
    path("support/", support, name="support"),
    path("publish-on-cash-matters/", write_for_us, name="write_for_us"),
    path("why-cash/", why_cash, name="why_cash"),
    path("why-cash-matters/", new_page, name="new_page"),

    path("django-admin/", admin.site.urls),

    # ✅ CUSTOM ADMIN URLS MUST BE ABOVE wagtailadmin_urls
    path("admin/all-blogs/", blogs_dashboard, name="blogs_dashboard_custom"),
    path("admin/blogs/add/", blogs_dashboard, name="blogs_dashboard"),
    path("admin/news/articles/", admin_views.admin_articles, name="admin_articles"),
    path("admin/news/key-facts/", admin_views.admin_keyfacts, name="admin_keyfacts"),

    # ✅ Wagtail admin include AFTER custom routes
    path("admin/", include(wagtailadmin_urls)),

    path("add-blog/", create_blog_page, name="create_blog_page"),
    path("blogs/add/", blogs_dashboard_redirect, name="blogs_dashboard_redirect"),
    path("documents/", include(wagtaildocs_urls)),
    path("api/v2/", api_router.urls),
    path("search/", search_views.search, name="search"),
    path("author/<str:author_name>/", author, name="author_profile"),
    path("author/id/<int:author_id>/", author, name="author_profile_by_id"),
    path("blog/admin/", include("blog.urls")),
    path("blog/support/", support, name="blog_support_redirect"),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]