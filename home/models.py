from django.db import models

from wagtail.models import Page


class HomePage(Page):
    subpage_types = [
        'blog.NewsIndexPage',
        'blog.BlogIndexPage',
        'blog.SupportPage',
        'blog.WhyCashMattersPage'
    ]
