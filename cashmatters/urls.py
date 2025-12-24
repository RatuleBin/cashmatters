from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
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
    """Serve the news page with dynamic articles and blog posts"""
    from blog.models import ArticlePage, BlogPage
    from itertools import chain

    # Get all published articles and blog posts
    articles = ArticlePage.objects.live().order_by('-date')
    blog_posts = BlogPage.objects.live().order_by('-date')

    # Combine and sort by date (newest first)
    combined_posts = sorted(
        chain(articles, blog_posts),
        key=lambda x: x.date,
        reverse=True
    )

    # Debug: Print posts and dates
    print(f"DEBUG: Total articles: {articles.count()}")
    print(f"DEBUG: Total blog posts: {blog_posts.count()}")
    print(f"DEBUG: Total combined posts: {len(combined_posts)}")
    for post in combined_posts[:5]:
        print(f"DEBUG: {post.title} - Date: {post.date} - Type: {post.__class__.__name__}")

    context = {
        'articles': combined_posts,  # Keep the same variable name for template compatibility
    }
    return render(request, 'news.html', context)


def author(request, author_name):
    """Serve the author profile page showing all articles by a specific author"""
    from blog.models import ArticlePage, BlogPage
    from itertools import chain

    # Get all published articles and blog posts by this author
    articles = ArticlePage.objects.live().filter(author__iexact=author_name).order_by('-date')
    blog_posts = BlogPage.objects.live().filter(author__iexact=author_name).order_by('-date')

    # Combine and sort by date (newest first)
    author_posts = sorted(
        chain(articles, blog_posts),
        key=lambda x: x.date,
        reverse=True
    )

    context = {
        'author_name': author_name,
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


def why_cash(request):
    """Serve the why cash page with dynamic content"""
    from blog.models import WhyCashMattersPage
    
    # Get the WhyCashMattersPage content
    page = WhyCashMattersPage.objects.live().first()
    
    context = {
        'page': page,
    }
    
    return render(request, 'why-cash.html', context)


def blogs_dashboard_redirect(request):
    """Redirect old blogs URL to new admin location"""
    return redirect('/admin/all-blogs/')


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


@staff_member_required
def blogs_dashboard(request):
    """Blog management dashboard"""
    from blog.models import BlogPage
    from django.db.models import Q
    from django.core.paginator import Paginator
    from django.contrib import messages
    from django.shortcuts import redirect

    # Handle bulk actions
    if request.method == 'POST':
        selected_posts = request.POST.getlist('selected_posts')
        bulk_action = request.POST.get('bulk_action')
        
        if selected_posts and bulk_action:
            posts = BlogPage.objects.filter(id__in=selected_posts)
            
            if bulk_action == 'publish':
                for post in posts:
                    if not post.live:
                        post.save_revision().publish()
                messages.success(
                    request, f"Published {len(selected_posts)} post(s)."
                )
            elif bulk_action == 'unpublish':
                for post in posts:
                    if post.live:
                        post.unpublish()
                messages.success(
                    request, f"Unpublished {len(selected_posts)} post(s)."
                )
            elif bulk_action == 'delete':
                count = posts.count()
                posts.delete()
                messages.success(request, f"Deleted {count} post(s).")
            
            return redirect(request.get_full_path())
    
    # Get search query
    search_query = request.GET.get('q', '')
    
    # Get filter parameters
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    location_filter = request.GET.get('location', '')
    sector_filter = request.GET.get('sector', '')
    
    # Base queryset - all blog pages
    blog_posts = BlogPage.objects.all().order_by('-date')
    
    # Apply search filter
    if search_query:
        blog_posts = blog_posts.filter(
            Q(title__icontains=search_query) |
            Q(intro__icontains=search_query) |
            Q(body__icontains=search_query)
        )
    
    # Apply category filter
    if category_filter:
        blog_posts = blog_posts.filter(article_types__name=category_filter)
    
    # Apply status filter
    if status_filter == 'live':
        blog_posts = blog_posts.filter(live=True)
    elif status_filter == 'draft':
        blog_posts = blog_posts.filter(live=False)
    
    # Apply location filter
    if location_filter:
        blog_posts = blog_posts.filter(locations__name=location_filter)
    
    # Apply sector filter
    if sector_filter:
        blog_posts = blog_posts.filter(sectors__name=sector_filter)
    
    # Remove duplicates from many-to-many filters
    blog_posts = blog_posts.distinct()
    
    # Pagination
    paginator = Paginator(blog_posts, 20)  # 20 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique values for filters
    categories = BlogPage.objects.values_list(
        'article_types__name', flat=True
    ).distinct().exclude(article_types__name__isnull=True)
    locations = BlogPage.objects.values_list(
        'locations__name', flat=True
    ).distinct().exclude(locations__name__isnull=True)
    sectors = BlogPage.objects.values_list(
        'sectors__name', flat=True
    ).distinct().exclude(sectors__name__isnull=True)
    
    # Stats
    total_posts = BlogPage.objects.count()
    live_posts = BlogPage.objects.filter(live=True).count()
    draft_posts = BlogPage.objects.filter(live=False).count()

    context = {
        'blog_posts': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'location_filter': location_filter,
        'sector_filter': sector_filter,
        'categories': sorted(set(categories)),
        'locations': sorted(set(locations)),
        'sectors': sorted(set(sectors)),
        'total_posts': total_posts,
        'live_posts': live_posts,
        'draft_posts': draft_posts,
        'paginator': paginator,
        'page_obj': page_obj,
    }
    return render(request, 'blogs_dashboard.html', context)


urlpatterns = [
    path("", index, name="index"),  # Root URL serves the homepage
    path("news/", news, name="news"),  # News page
    path("support/", support, name="support"),  # Support page
    path("why-cash/", why_cash, name="why_cash"),  # Why cash page
    path("django-admin/", admin.site.urls),
    path("admin/all-blogs/", blogs_dashboard, name="blogs_dashboard_custom"),
    path("add-blog/", create_blog_page, name="create_blog_page"),
    path("admin/", include(wagtailadmin_urls)),
    path("admin/blogs/add/", blogs_dashboard, name="blogs_dashboard"),
    # Blog creation dashboard
    path("blogs/add/", blogs_dashboard_redirect,
         name="blogs_dashboard_redirect"),  # Redirect old URL
    path("documents/", include(wagtaildocs_urls)),
    path("api/v2/", api_router.urls),
    path("search/", search_views.search, name="search"),
    path("author/<str:author_name>/", author, name="author_profile"),
    path("blog/admin/", include("blog.urls")),  # Blog app URLs
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
