from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from wagtail.models import Page
from .models import NewsIndexPage

@staff_member_required
def admin_articles(request):
    page = NewsIndexPage.objects.first() or Page.objects.filter(slug="news").first()
    if page:
        return redirect(reverse("wagtailadmin_explore", args=[page.id]))
    return redirect(reverse("wagtailadmin_home"))

@staff_member_required
def admin_keyfacts(request):
    page = NewsIndexPage.objects.first() or Page.objects.filter(slug="news").first()
    if page:
        return redirect(reverse("wagtailadmin_explore", args=[page.id]))
    return redirect(reverse("wagtailadmin_home"))
