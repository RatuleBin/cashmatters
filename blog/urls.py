# blog/urls.py
from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("create/", views.create_blog_post, name="create_blog_post"),

    path("create-article/", views.create_article_post, name="create_article_post"),
    path("create-key-facts/", views.create_key_facts_post, name="create_key_facts_post"),

    path("support/", views.create_support_page, name="create_support_page"),
    path("why-cash/", views.create_why_cash_matters_page, name="create_why_cash_matters_page"),
    path("feature-page/", views.create_why_cash_feature_page, name="create_why_cash_feature_page"),
]
