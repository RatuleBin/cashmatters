from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.ui.components import Component
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from django.urls import reverse, path
from django.utils.html import format_html
from django.shortcuts import redirect
from .models import BlogPage, WhyCashMattersPage, SupportPage, Author


class AuthorViewSet(SnippetViewSet):
    """Custom ViewSet for Author snippet with article count column"""
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


@hooks.register('register_admin_menu_item')
def register_blogs_dashboard_menu_item():
    return MenuItem(
        'Blogs Dashboard',
        '/admin/all-blogs/',
        icon_name='list-ul',
        order=9999
    )


@hooks.register('register_admin_menu_item')
def register_support_page_menu_item():
    return MenuItem(
        'Support Cash Page',
        reverse('blog:create_support_page'),
        icon_name='help',
        order=10001
    )


@hooks.register('register_admin_menu_item')
def register_why_cash_feature_page_menu_item():
    return MenuItem(
        'Why Cash Feature Page',
        reverse('blog:create_why_cash_feature_page'),
        icon_name='doc-full-inverse',
        order=10003
    )


@hooks.register('construct_main_menu')
def hide_unwanted_menu_items(request, menu_items):
    """Hide all menu items except Blogs Dashboard, Support Cash Page, Why Cash Feature Page, and Images"""
    allowed_items = [
        'Blogs Dashboard',
        'Support Cash Page',
        'Why Cash Feature Page',
        'images',  # Wagtail's built-in images menu
    ]
    menu_items[:] = [
        item for item in menu_items
        if item.name in allowed_items or item.label in allowed_items
    ]


@hooks.register('insert_global_admin_js')
def global_admin_js():
    """Add JS to redirect to blogs dashboard after saving a blog post"""
    # Using Wagtail hooks instead for better reliability
    return ""


@hooks.register('after_edit_page')
def redirect_after_blog_edit(request, page):
    """Redirect to blogs dashboard after editing a blog post"""
    if isinstance(page, BlogPage):
        from django.shortcuts import redirect
        return redirect('/admin/all-blogs/')


@hooks.register('after_create_page')
def redirect_after_blog_create(request, page):
    """Redirect to blogs dashboard after creating a blog post"""
    if isinstance(page, BlogPage):
        from django.shortcuts import redirect
        return redirect('/admin/all-blogs/')


class AddBlogButton(Component):
    def render_html(self, parent_context):
        page = parent_context.get('page')
        if page and hasattr(page, 'slug') and page.slug == 'news':
            return format_html(
                '<a href="{}" class="button button--primary">'
                '<svg class="icon icon-plus icon--white" aria-hidden="true">'
                '<use href="#icon-plus"></use></svg>'
                'Add Blog Post</a>',
                reverse('blog:create_blog_post',
                        kwargs={'parent_page_id': page.id})
            )
        return ''


@hooks.register('register_page_listing_more_buttons')
def add_blog_button(page, user, next_url=None):
    if page.slug == 'news':
        from wagtail.admin.widgets import Button
        from django.urls import reverse

        button = Button(
            'Add Blog Post',
            reverse('blog:create_blog_post',
                    kwargs={'parent_page_id': page.id}),
            priority=10,
            icon_name='plus'
        )
        return [button]
    return []


@hooks.register('before_create_page')
def redirect_why_cash_matters_to_edit(request, page_class, parent):
    """Redirect WhyCashMattersPage creation to edit existing page"""
    if page_class == WhyCashMattersPage:
        existing_page = WhyCashMattersPage.objects.live().first()
        if existing_page:
            # Redirect to edit the existing page
            edit_url = reverse('wagtailadmin_pages:edit',
                               args=[existing_page.id])
            return redirect(edit_url)
    return None


@hooks.register('register_admin_urls')
def custom_why_cash_matters_urls():
    """Custom URL patterns for WhyCashMattersPage singleton behavior"""
    from wagtail.admin.views.pages.create import CreateView
    from django.shortcuts import redirect
    from django.urls import reverse
    
    # Monkey patch the CreateView dispatch method
    original_dispatch = CreateView.dispatch
    
    def patched_dispatch(self, request, content_type_app_name,
                         content_type_model_name, parent_page_id):
        if (content_type_app_name == 'blog' and
                content_type_model_name in ['whycashmatterspage',
                                            'supportpage']):
            # Check for existing page based on model type
            if content_type_model_name == 'whycashmatterspage':
                existing_page = WhyCashMattersPage.objects.live().first()
            elif content_type_model_name == 'supportpage':
                existing_page = SupportPage.objects.live().first()
            
            if existing_page:
                # Redirect to edit the existing page
                edit_url = reverse('wagtailadmin_pages:edit',
                                   args=[existing_page.id])
                return redirect(edit_url)
        # Fall back to default behavior
        return original_dispatch(self, request, content_type_app_name,
                                 content_type_model_name, parent_page_id)
    
    CreateView.dispatch = patched_dispatch
    
    # Custom URL for direct access to WhyCashMattersPage edit
    def why_cash_matters_edit_redirect(request):
        """Redirect to edit the existing WhyCashMattersPage"""
        existing_page = WhyCashMattersPage.objects.live().first()
        if existing_page:
            edit_url = reverse('wagtailadmin_pages:edit',
                               args=[existing_page.id])
            return redirect(edit_url)
        else:
            # If no page exists, redirect to create
            return redirect(reverse('wagtailadmin_home'))
    
    # Custom URL for direct access to SupportPage edit
    def support_page_edit_redirect(request):
        """Redirect to edit the existing SupportPage"""
        existing_page = SupportPage.objects.live().first()
        if existing_page:
            edit_url = reverse('wagtailadmin_pages:edit',
                               args=[existing_page.id])
            return redirect(edit_url)
        else:
            # If no page exists, redirect to create
            return redirect(reverse('wagtailadmin_home'))
    
    return [
        path('why-cash-matters/',
             why_cash_matters_edit_redirect,
             name='why_cash_matters_edit'),
        path('support/',
             support_page_edit_redirect,
             name='support_page_edit'),
    ]


@hooks.register('construct_page_listing_buttons')
def modify_add_button_for_homepage(buttons, page, user, context):
    """Modify add buttons for HomePage to handle WhyCashMattersPage"""
    if page.__class__.__name__ == 'HomePage':
        # Check if WhyCashMattersPage already exists
        existing_page = WhyCashMattersPage.objects.live().first()
        if existing_page:
            # Remove the original add button for WhyCashMattersPage
            buttons[:] = [btn for btn in buttons
                          if not (hasattr(btn, 'label') and
                                  'Why Cash Matters Page' in str(btn.label))]
            
            # Add an edit button instead
            from wagtail.admin.widgets import Button
            
            edit_button = Button(
                'Edit Why Cash Matters Page',
                '/admin/why-cash-matters/',
                priority=10,
                icon_name='edit'
            )
            buttons.append(edit_button)
    
    return buttons
