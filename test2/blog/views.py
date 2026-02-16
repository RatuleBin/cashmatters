from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from wagtail.images import get_image_model
from wagtail.rich_text import RichText
from .forms import BlogPostForm
from .models import BlogIndexPage, BlogPage, SupportPage, WhyCashMattersPage
from .models import WhyCashMattersFeaturePage
import json
from django.shortcuts import redirect
from wagtail.admin.auth import permission_required
from wagtail.models import Page

from .models import BlogIndexPage

def content_blocks_to_html(blocks):
    """Convert content blocks to HTML"""
    html_parts = []

    for block in blocks:
        block_type = block.get('type')

        if block_type == 'content':
            content = block.get('content', '').strip()
            if content:
                html_parts.append('<p>{}</p>'.format(content))

        elif block_type == 'image_caption':
            caption = block.get('caption', '').strip()
            if caption:
                html_parts.append(
                    '<figure><img src="#" alt="{}">'
                    '<figcaption>{}</figcaption></figure>'.format(
                        caption, caption))

        elif block_type == 'video_caption':
            caption = block.get('caption', '').strip()
            if caption:
                html_parts.append(
                    '<figure><video controls><source src="#" '
                    'type="video/mp4"></video>'
                    '<figcaption>{}</figcaption></figure>'.format(caption))

        elif block_type == 'iframe_caption':
            url = block.get('url', '').strip()
            caption = block.get('caption', '').strip()
            if url:
                iframe_html = ('<iframe src="{}" width="100%" '
                              'height="400" frameborder="0"></iframe>'.format(
                                  url))
                if caption:
                    iframe_html = ('<figure>{}<figcaption>{}</figcaption>'
                                  '</figure>'.format(iframe_html, caption))
                html_parts.append(iframe_html)

        elif block_type == 'blockquote':
            quote = block.get('quote', '').strip()
            author = block.get('author', '').strip()
            if quote:
                blockquote_html = '<blockquote><p>{}</p>'.format(quote)
                if author:
                    blockquote_html += '<cite>— {}</cite>'.format(author)
                blockquote_html += '</blockquote>'
                html_parts.append(blockquote_html)

        elif block_type == 'data_table':
            table_data = block.get('table_data', '').strip()
            if table_data:
                # Simple CSV to table conversion
                try:
                    rows = [line.split(',') for line in
                           table_data.split('\n') if line.strip()]
                    if rows:
                        table_html = '<table><tbody>'
                        for row in rows:
                            table_html += '<tr>'
                            for cell in row:
                                table_html += '<td>{}</td>'.format(
                                    cell.strip())
                            table_html += '</tr>'
                        table_html += '</tbody></table>'
                        html_parts.append(table_html)
                except (ValueError, IndexError):
                    html_parts.append('<pre>{}</pre>'.format(table_data))

        elif block_type == 'poll':
            question = block.get('question', '').strip()
            options = block.get('options', '').strip()
            if question:
                poll_html = '<div class="poll"><h3>{}</h3>'.format(question)
                if options:
                    poll_html += '<ul>'
                    for option in options.split('\n'):
                        option = option.strip()
                        if option:
                            poll_html += '<li>{}</li>'.format(option)
                    poll_html += '</ul>'
                poll_html += '</div>'
                html_parts.append(poll_html)

        elif block_type == 'facts_carousel':
            facts = block.get('facts', '').strip()
            if facts:
                try:
                    facts_list = json.loads(facts)
                    if isinstance(facts_list, list):
                        carousel_html = '<div class="facts-carousel">'
                        for fact in facts_list:
                            carousel_html += ('<div class="fact-item">'
                                            '{}</div>'.format(fact))
                        carousel_html += '</div>'
                        html_parts.append(carousel_html)
                except (json.JSONDecodeError, TypeError):
                    html_parts.append('<pre>{}</pre>'.format(facts))

        elif block_type == 'key_fact_image':
            fact = block.get('fact', '').strip()
            if fact:
                html_parts.append(
                    '<div class="key-fact"><img src="#" alt="Key fact">'
                    '<p>{}</p></div>'.format(fact))

    return '\n'.join(html_parts)


@permission_required("wagtailadmin.access_admin")
def create_blog_post(request):
    """
    Create BlogPage under BlogIndexPage and redirect to Wagtail admin add screen.
    """
    parent = BlogIndexPage.objects.first()
    if not parent:
        root = Page.get_first_root_node()
        parent = BlogIndexPage(title="Blog", slug="blog", intro="Welcome to our blog")
        root.add_child(instance=parent)
        parent.save_revision().publish()

    # Wagtail add URL
    return redirect(f"/admin/pages/add/blog/blogpage/{parent.id}/?next=/admin/all-blogs/")


@login_required
@login_required
def create_support_page(request):
    """Create or edit SupportPage (singleton) - redirects to Wagtail admin"""
    from wagtail.models import Page
    from django.contrib import messages

    try:
        # First check if there's any page with slug "support" (regardless of type)
        existing_page = Page.objects.filter(slug="support").first()
        if existing_page:
            # Redirect to edit the existing page
            return redirect(f'/admin/pages/{existing_page.id}/edit/')

        # Check if a SupportPage already exists (look for slug "support")
        existing_support_page = SupportPage.objects.filter(slug="support").first()
        if existing_support_page:
            # Redirect to edit the existing page
            return redirect(f'/admin/pages/{existing_support_page.id}/edit/')

        # If no page exists, create one under the root page
        root_page = Page.objects.get(id=1)  # Root page
        support_page = SupportPage(
            title="Support",
            slug="support",
            page_header_title="Support Cash"
        )
        root_page.add_child(instance=support_page)
        support_page.save()
        print(f"Created new SupportPage with ID: {support_page.id}")

        # Redirect to edit the newly created page
        return redirect(f'/admin/pages/{support_page.id}/edit/')

    except Exception as e:
        messages.error(request, f"Error setting up support page: {e}")
        return redirect('/admin/')


@login_required
def create_why_cash_matters_page(request):
    """Create or edit WhyCashMattersPage (singleton)"""
    from wagtail.models import Page
    from django.contrib import messages
    from datetime import date

    try:
        # First check if there's any page with slug "why-cash" (regardless of type)
        existing_page = Page.objects.filter(slug="why-cash").first()
        if existing_page:
            # Redirect to edit the existing page
            return redirect(f'/admin/pages/{existing_page.id}/edit/')

        # Check if a WhyCashMattersPage already exists (look for slug "why-cash")
        existing_why_page = WhyCashMattersPage.objects.filter(slug="why-cash").first()
        if existing_why_page:
            # Redirect to edit the existing page
            return redirect(f'/admin/pages/{existing_why_page.id}/edit/')

        # If no page exists, create one under the root page
        root_page = Page.objects.get(id=1)  # Root page
        why_cash_page = WhyCashMattersPage(
            title="Why Cash Matters",
            slug="why-cash",
            date=date.today(),
            intro="Understanding the importance of cash in today's economy"
        )
        root_page.add_child(instance=why_cash_page)
        why_cash_page.save()
        print(f"Created new WhyCashMattersPage with ID: {why_cash_page.id}")

        # Redirect to edit the newly created page
        return redirect(f'/admin/pages/{why_cash_page.id}/edit/')

    except Exception as e:
        messages.error(request, f"Error setting up why cash matters page: {e}")
        return redirect('/admin/')


@login_required
def create_why_cash_feature_page(request):
    """Create or edit WhyCashMattersFeaturePage (singleton) - for new-page URL"""
    from wagtail.models import Page
    from django.contrib import messages

    # Check if a WhyCashMattersFeaturePage already exists
    existing_feature_page = WhyCashMattersFeaturePage.objects.first()
    if existing_feature_page:
        # Redirect to edit the existing page
        return redirect(f'/admin/pages/{existing_feature_page.id}/edit/')

    # If no page exists, create one under the root page
    try:
        root_page = Page.objects.get(id=1)  # Root page
        feature_page = WhyCashMattersFeaturePage(
            title="Why Cash Matters Feature",
            slug="new-page",
            page_title="Why Cash Matters",
            page_date="Apr 1, 2025",
            intro_text="New technologies are changing the way we pay, and cash remains the most attractive option for many."
        )
        root_page.add_child(instance=feature_page)
        feature_page.save_revision().publish()
        messages.success(request, f"Successfully created Why Cash Matters Feature Page!")

        # Redirect to edit the newly created page
        return redirect(f'/admin/pages/{feature_page.id}/edit/')

    except Exception as e:
        messages.error(request, f"Error setting up feature page: {e}")
        return redirect('/admin/')
