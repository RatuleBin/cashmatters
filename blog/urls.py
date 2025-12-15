from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('create/<int:parent_page_id>/', views.create_blog_post, name='create_blog_post'),
]
