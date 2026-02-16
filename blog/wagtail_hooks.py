# blog/wagtail_hooks.py

from django.shortcuts import redirect
from django.urls import reverse, path

from wagtail import hooks
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem
from wagtail.admin.widgets import Button
from wagtail.models import Page

from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.snippets.models import register_snippet

from .models import BlogPage, WhyCashMattersPage, SupportPage, Author, NewsIndexPage


# ----------------------------
# Config
# ----------------------------
NEWS_INDEX_SLUG = "news"


# ----------------------------
# Snippet: Authors
# ----------------------------
class AuthorViewSet(SnippetViewSet):
    model = Author
    icon = "user"
    menu_label = "Authors"
    menu_name = "authors"
    menu_order = 200
    add_to_admin_menu = True

    list_display = ["name", "job_title", "get_article_count"]
    list_filter = ["job_title"]
    search_fields = ["name", "job_title", "bio"]


register_snippet(AuthorViewSet)


# ----------------------------
# Helpers
# ----------------------------
def _get_news_index_id():
    try:
        page = NewsIndexPage.objects.first()
        if page:
            return page.id
    except Exception:
        pass

    page = Page.objects.filter(slug=NEWS_INDEX_SLUG).first()
    return page.id if page else None


# ----------------------------
# Admin menu items
# ----------------------------
@hooks.register("register_admin_menu_item")
def register_blogs_dashboard_menu_item():
    return MenuItem(
        "Blogs Dashboard",
        reverse("blogs_dashboard_custom"),
        icon_name="list-ul",
        order=9001,
    )


@hooks.register("register_admin_menu_item")
def register_news_articles_submenu():
    submenu = Menu(items=[
        MenuItem("Articles", reverse("admin_articles"), icon_name="doc-full", order=1),
        MenuItem("Key Facts", reverse("admin_keyfacts"), icon_name="pick", order=2),
    ])

    return SubmenuMenuItem(
        "News & Articles",
        submenu,
        icon_name="folder-open-inverse",
        order=9000,
    )


@hooks.register("register_admin_menu_item")
def register_support_page_menu_item():
    return MenuItem(
        "Support Cash",
        reverse("blog:create_support_page"),
        icon_name="help",
        order=9002,
    )


@hooks.register("register_admin_menu_item")
def register_why_cash_feature_page_menu_item():
    return MenuItem(
        "Why Cash Feature Page",
        reverse("blog:create_why_cash_feature_page"),
        icon_name="doc-full-inverse",
        order=9003,
    )


# ----------------------------
# Redirect after save for BlogPage
# ----------------------------
@hooks.register("after_edit_page")
def redirect_after_blog_edit(request, page):
    if isinstance(page, BlogPage):
        return redirect("/admin/all-blogs/")


@hooks.register("after_create_page")
def redirect_after_blog_create(request, page):
    if isinstance(page, BlogPage):
        return redirect("/admin/all-blogs/")


# ----------------------------
# Listing "more" buttons (Explorer)
# ----------------------------
@hooks.register("register_page_listing_more_buttons")
def add_listing_buttons(page, user, next_url=None):
    # NewsIndexPage -> show Article + Key Facts buttons
    if isinstance(page, NewsIndexPage):
        return [
            Button("Add Article", reverse("blog:create_article_post"), priority=10, icon_name="plus"),
            Button("Add Key Facts", reverse("blog:create_key_facts_post"), priority=11, icon_name="plus"),
        ]

    # BlogIndex (slug blog) -> Add Blog Post
    if getattr(page, "slug", None) == "blog":
        return [
            Button("Add Blog Post", reverse("blog:create_blog_post"), priority=10, icon_name="plus"),
        ]

    return []


# ----------------------------
# Singleton behavior (SupportPage / WhyCashMattersPage)
# ----------------------------
@hooks.register("before_create_page")
def prevent_duplicate_singletons(request, page_class, parent):
    if page_class == WhyCashMattersPage:
        existing = WhyCashMattersPage.objects.live().first()
        if existing:
            return redirect(reverse("wagtailadmin_pages:edit", args=[existing.id]))

    if page_class == SupportPage:
        existing = SupportPage.objects.live().first()
        if existing:
            return redirect(reverse("wagtailadmin_pages:edit", args=[existing.id]))

    return None


@hooks.register("register_admin_urls")
def register_singleton_shortcuts():
    def why_cash_matters_edit_redirect(request):
        existing = WhyCashMattersPage.objects.live().first()
        if existing:
            return redirect(reverse("wagtailadmin_pages:edit", args=[existing.id]))
        return redirect(reverse("wagtailadmin_home"))

    def support_page_edit_redirect(request):
        existing = SupportPage.objects.live().first()
        if existing:
            return redirect(reverse("wagtailadmin_pages:edit", args=[existing.id]))
        return redirect(reverse("wagtailadmin_home"))

    return [
        path("why-cash-matters/", why_cash_matters_edit_redirect, name="why_cash_matters_edit"),
        path("support/", support_page_edit_redirect, name="support_page_edit"),
    ]


