from django.contrib import admin
from .models import ArticleType, Location, Sector, ArticlePage, KeyFactsPage


# Register supporting models in Django admin
admin.site.register(ArticleType)
admin.site.register(Location)
admin.site.register(Sector)


# Note: ArticlePage is a Wagtail Page model and should be
# managed through Wagtail admin
