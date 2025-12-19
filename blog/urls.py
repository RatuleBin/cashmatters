from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('create/', views.create_blog_post, name='create_blog_post'),
    path('support/', views.create_support_page, name='create_support_page'),
    path('why-cash/', views.create_why_cash_matters_page,
         name='create_why_cash_matters_page'),
]
