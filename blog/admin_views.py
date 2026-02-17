from django.shortcuts import redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from wagtail.models import Page
from .models import NewsIndexPage, KeyFactsPage


@staff_member_required
def admin_articles(request):
    page = NewsIndexPage.objects.first() or Page.objects.filter(slug="news").first()
    if page:
        return redirect(reverse("wagtailadmin_explore", args=[page.id]))
    return redirect(reverse("wagtailadmin_home"))


@staff_member_required
def admin_keyfacts(request):
    """Custom admin listing for Key Facts pages with direct edit links."""
    key_facts = KeyFactsPage.objects.all().order_by('-date', '-first_published_at')

    # Find the parent page for "Add" button
    parent = NewsIndexPage.objects.first() or Page.objects.filter(slug="news").first()
    add_url = None
    if parent:
        add_url = reverse(
            "wagtailadmin_pages:add",
            kwargs={
                "content_type_app_name": "blog",
                "content_type_model_name": "keyfactspage",
                "parent_page_id": parent.id,
            },
        )

    context = {
        "key_facts": key_facts,
        "add_url": add_url,
    }
    return render(request, "admin/key_facts_listing.html", context)
