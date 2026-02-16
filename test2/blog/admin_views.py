from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from wagtail.admin.auth import permission_required
from wagtail.models import Page

from .models import BlogPage, ArticlePage, SupportPage, WhyCashMattersPage, WhyCashMattersFeaturePage


def _get_root():
    # Ավելի ճիշտ, քան id=1
    return Page.get_first_root_node()


@permission_required("wagtailadmin.access_admin")
def all_blogs_dashboard(request):
    blogs = BlogPage.objects.live().order_by("-first_published_at")
    articles = ArticlePage.objects.live().order_by("-first_published_at")
    return render(
        request,
        "wagtailadmin/blog/all_blogs_dashboard.html",
        {"blogs": blogs, "articles": articles},
    )


@permission_required("wagtailadmin.access_admin")
def support_singleton(request):
    page = SupportPage.objects.first()
    if page:
        return redirect(reverse("wagtailadmin_pages:edit", args=[page.id]))

    root = _get_root()
    page = SupportPage(title="Support", slug="support", page_header_title="Support Cash")
    root.add_child(instance=page)
    page.save_revision().publish()
    messages.success(request, "Support page created.")
    return redirect(reverse("wagtailadmin_pages:edit", args=[page.id]))


@permission_required("wagtailadmin.access_admin")
def why_cash_singleton(request):
    page = WhyCashMattersPage.objects.first()
    if page:
        return redirect(reverse("wagtailadmin_pages:edit", args=[page.id]))

    root = _get_root()
    page = WhyCashMattersPage(title="Why Cash Matters", slug="why-cash", intro="Why cash matters")
    root.add_child(instance=page)
    page.save_revision().publish()
    messages.success(request, "Why Cash Matters page created.")
    return redirect(reverse("wagtailadmin_pages:edit", args=[page.id]))


@permission_required("wagtailadmin.access_admin")
def why_cash_feature_singleton(request):
    page = WhyCashMattersFeaturePage.objects.first()
    if page:
        return redirect(reverse("wagtailadmin_pages:edit", args=[page.id]))

    root = _get_root()
    page = WhyCashMattersFeaturePage(
        title="Why Cash Matters Feature",
        slug="new-page",
        page_title="Why Cash Matters",
        page_date="Apr 1, 2025",
        intro_text="New technologies are changing the way we pay, and cash remains important.",
    )
    root.add_child(instance=page)
    page.save_revision().publish()
    messages.success(request, "Feature page created.")
    return redirect(reverse("wagtailadmin_pages:edit", args=[page.id]))
