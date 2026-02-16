# blog/wagtail_hooks.py

from django.shortcuts import redirect
from django.urls import reverse, path
from django.utils.html import format_html

from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.ui.components import Component
from wagtail.models import Page

from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.snippets.models import register_snippet

from .models import BlogPage, WhyCashMattersPage, SupportPage, Author
from .models import NewsIndexPage  # IMPORTANT: համոզվի, որ սա կա քո models-ում


# ----------------------------
# Config (կարող ես փոխել)
# ----------------------------
NEWS_INDEX_SLUG = "news"  # եթե քո NewsIndexPage-ի slug-ը ուրիշ է՝ փոխիր այստեղ


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


# NOTE:
# Եթե քո Wagtail version-ում register_snippet(viewset) չի աշխատում,
# փոխիր սա դեպի `register_snippet(Author)` և թողնես Author-ի panels-ը model-ում։
register_snippet(AuthorViewSet)


# ----------------------------
# Helpers
# ----------------------------
def _get_news_index_page_id():
    page = Page.objects.type(NewsIndexPage).filter(slug=NEWS_INDEX_SLUG).first()
    if page:
        return page.id
    page = Page.objects.type(NewsIndexPage).first()
    return page.id if page else None



# ----------------------------
# Custom menu items
# ----------------------------
@hooks.register("register_admin_menu_item")
def register_blogs_dashboard_menu_item():
    return MenuItem(
        "Blogs Dashboard",
        "/admin/all-blogs/",
        icon_name="list-ul",
        order=9999,
    )


@hooks.register("register_admin_menu_item")
def register_support_page_menu_item():
    return MenuItem(
        "Support Cash",
        reverse("blog:create_support_page"),
        icon_name="help",
        order=10001,
    )


@hooks.register("register_admin_menu_item")
def register_why_cash_feature_page_menu_item():
    return MenuItem(
        "Why Cash Feature Page",
        reverse("blog:create_why_cash_feature_page"),
        icon_name="doc-full-inverse",
        order=10003,
    )


@hooks.register("register_admin_menu_item")
def register_news_articles_menu_item():
    """
    Menu item that opens the correct 'News & Articles' section,
    without hardcoding args=[3].
    """
    page_id = _get_news_index_page_id()
    if not page_id:
        # fallback՝ թող գնա Pages home
        return MenuItem(
            "News & Articles",
            reverse("wagtailadmin_explore_root"),
            icon_name="folder-open-1",
            order=120,
        )

    return MenuItem(
        "News & Articles",
        reverse("wagtailadmin_explore", args=[page_id]),
        icon_name="folder-open-1",
        order=120,
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
# Add button on listing (optional)
# ----------------------------
class AddBlogButton(Component):
    def render_html(self, parent_context):
        page = parent_context.get("page")
        if page and getattr(page, "slug", None) == NEWS_INDEX_SLUG:
            return format_html(
                '<a href="{}" class="button button--primary">'
                '<svg class="icon icon-plus icon--white" aria-hidden="true">'
                '<use href="#icon-plus"></use></svg>'
                "Add Blog Post</a>",
                reverse('blog:create_blog_post')

            )
        return ""


@hooks.register("register_page_listing_more_buttons")
def add_blog_button(page, user, next_url=None):
    if getattr(page, "slug", None) == NEWS_INDEX_SLUG:
        from wagtail.admin.widgets import Button

        button = Button(
            "Add Blog Post",
            reverse('blog:create_blog_post'),
            priority=10,
            icon_name="plus",
        )
        return [button]
    return []


# ----------------------------
# Singleton behavior (safe)
# ----------------------------
@hooks.register("before_create_page")
def prevent_duplicate_singletons(request, page_class, parent):
    """
    Prevent creating 2nd SupportPage / WhyCashMattersPage.
    Instead redirect to edit existing live page.
    """
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
    """
    Friendly shortcut URLs inside admin:
      /admin/why-cash-matters/ -> edit existing WhyCashMattersPage
      /admin/support/ -> edit existing SupportPage
    """

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


# ----------------------------
# HomePage add-button tweak (optional)
# ----------------------------
@hooks.register("construct_page_listing_buttons")
def modify_add_button_for_homepage(buttons, page, user, context):
    """
    If HomePage tries to show 'Add Why Cash Matters Page' and it already exists,
    remove add and show edit shortcut instead.
    """
    if page.__class__.__name__ != "HomePage":
        return buttons

    existing = WhyCashMattersPage.objects.live().first()
    if not existing:
        return buttons

    # remove any button that contains label 'Why Cash Matters'
    buttons[:] = [
        btn
        for btn in buttons
        if not (hasattr(btn, "label") and "Why Cash Matters" in str(btn.label))
    ]

    from wagtail.admin.widgets import Button

    buttons.append(
        Button(
            "Edit Why Cash Matters Page",
            "/admin/why-cash-matters/",
            priority=10,
            icon_name="edit",
        )
    )
    return buttons


# ----------------------------
# Optional: hide unwanted main menu items
# ----------------------------
# @hooks.register("construct_main_menu")
# def hide_unwanted_menu_items(request, menu_items):
#     allowed = {
#         "Blogs Dashboard",
#         "Support Cash",
#         "Why Cash Feature Page",
#         "News & Articles",
#         "Images",
#         "Authors",
#     }
#     menu_items[:] = [
#         item
#         for item in menu_items
#         if (getattr(item, "label", None) in allowed) or (getattr(item, "name", None) in allowed)
#     ]


from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.snippets.models import register_snippet

from .models import Author, ArticleType, Location, Sector

# ----------------------------
# Existing: Authors (OK)
# ----------------------------


# ----------------------------
# NEW: Article Types
# ----------------------------
class ArticleTypeViewSet(SnippetViewSet):
    model = ArticleType
    icon = "tag"
    menu_label = "Article Types"
    menu_name = "article-types"
    menu_order = 210
    add_to_admin_menu = True

    list_display = ["name"]
    search_fields = ["name"]


register_snippet(ArticleTypeViewSet)

# ----------------------------
# NEW: Locations
# ----------------------------
class LocationViewSet(SnippetViewSet):
    model = Location
    icon = "site"
    menu_label = "Locations"
    menu_name = "locations"
    menu_order = 220
    add_to_admin_menu = True

    list_display = ["name"]
    search_fields = ["name"]


register_snippet(LocationViewSet)

# ----------------------------
# NEW: Sectors
# ----------------------------
class SectorViewSet(SnippetViewSet):
    model = Sector
    icon = "folder-open-1"
    menu_label = "Sectors"
    menu_name = "sectors"
    menu_order = 230
    add_to_admin_menu = True

    list_display = ["name"]
    search_fields = ["name"]


register_snippet(SectorViewSet)