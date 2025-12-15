from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.ui.components import Component
from django.urls import reverse
from django.utils.html import format_html


@hooks.register('register_admin_menu_item')
def register_news_and_article_menu_item():
    return MenuItem(
        'News & Articles',
        '/admin/pages/10/',
        icon_name='doc-full',
        order=10000
    )


@hooks.register('register_admin_menu_item')
def register_blogs_dashboard_menu_item():
    return MenuItem(
        'Blogs Dashboard',
        '/admin/blogs/add/',
        icon_name='list-ul',
        order=9999
    )


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
