from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render, redirect
import os

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views
from blog.api import api_router

# Frontend views
def index(request):
    """Serve the homepage"""
    return render(request, 'index.html')


def news(request):
    """Serve the news page with dynamic articles"""
    from blog.models import ArticlePage
    
    # Get all published articles ordered by date (newest first)
    articles = ArticlePage.objects.live().order_by('-date')
    
    # Debug: Print articles and dates
    print(f"DEBUG: Total articles: {articles.count()}")
    for article in articles[:5]:
        print(f"DEBUG: {article.title} - Date: {article.date}")
    
    context = {
        'articles': articles,
    }
    return render(request, 'news.html', context)


def support(request):
    """Serve the support page"""
    return render(request, 'support.html')


def why_cash(request):
    """Serve the why cash page"""
    return render(request, 'why-cash.html')


def blogs_dashboard_redirect(request):
    """Redirect old blogs URL to new admin location"""
    return redirect('/admin/blogs/add/')


def blogs_dashboard(request):
    """Blog management dashboard"""
    from blog.models import NewsIndexPage, ArticlePage

    try:
        news_index = NewsIndexPage.objects.get(slug='news')
        # Get all published blog posts
        blog_posts = (ArticlePage.objects.live()
                      .order_by('-first_published_at')[:10])
    except NewsIndexPage.DoesNotExist:
        blog_posts = []

    context = {
        'blog_posts': blog_posts,
        'news_index': news_index if 'news_index' in locals() else None,
    }
    return render(request, 'blogs_dashboard.html', context)


urlpatterns = [
    path("", index, name="index"),  # Root URL serves the homepage
    path("news/", news, name="news"),  # News page
    path("support/", support, name="support"),  # Support page
    path("why-cash/", why_cash, name="why_cash"),  # Why cash page
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("admin/blogs/add/", blogs_dashboard, name="blogs_dashboard"),
    # Blog creation dashboard
    path("blogs/add/", blogs_dashboard_redirect,
         name="blogs_dashboard_redirect"),  # Redirect old URL
    path("documents/", include(wagtaildocs_urls)),
    path("api/v2/", api_router.urls),
    path("search/", search_views.search, name="search"),
    path("blog/", include("blog.urls")),  # Blog app URLs
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
