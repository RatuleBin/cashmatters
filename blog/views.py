from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from wagtail.images import get_image_model
from wagtail.rich_text import RichText
from .forms import BlogPostForm
from .models import BlogIndexPage, BlogPage
import json


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


@login_required
def create_blog_post(request, parent_page_id):
    """View to create a new blog post from the frontend"""
    
    try:
        parent_page = BlogIndexPage.objects.get(id=parent_page_id)
    except BlogIndexPage.DoesNotExist:
        messages.error(request, "Blog page not found.")
        return redirect('/admin/')
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle image uploads first
            Image = get_image_model()
            uploaded_images = {}
            
            # Process each image upload field
            image_fields = [
                ('tall_thumbnail_upload', 'tall_thumbnail'),
                ('wide_thumbnail_upload', 'wide_thumbnail'),
                ('page_header_image_upload', 'page_header_image'),
                ('icon_upload', 'icon')
            ]
            
            for upload_field, model_field in image_fields:
                if form.cleaned_data.get(upload_field):
                    # Create Wagtail image from uploaded file
                    image_file = form.cleaned_data[upload_field]
                    image = Image.objects.create(
                        title=image_file.name,
                        file=image_file
                    )
                    uploaded_images[model_field] = image
            
            # Create the blog page instance with all fields
            # Convert content blocks to HTML for the body field
            content_blocks = form.cleaned_data.get('content_blocks', [])
            body_html = content_blocks_to_html(content_blocks)
            
            blog_post = BlogPage(
                title=form.cleaned_data['title'],
                date=form.cleaned_data['date'],
                intro=form.cleaned_data['intro'],
                body=RichText(body_html),
                title_position=form.cleaned_data.get('title_position', ''),
                page_header=form.cleaned_data.get('page_header', ''),
                featured=form.cleaned_data.get('featured', False),
                double_width=form.cleaned_data.get('double_width', False),
                white_text=form.cleaned_data.get('white_text', False),
                hide_title=form.cleaned_data.get('hide_title', False),
                color=form.cleaned_data.get('color', ''),
                cm_watermark=form.cleaned_data.get('cm_watermark', False),
                alternative_text=form.cleaned_data.get('alternative_text', ''),
                twitter_body=form.cleaned_data.get('twitter_body', ''),
                vimeo_id=form.cleaned_data.get('vimeo_id', ''),
                source_link=form.cleaned_data.get('source_link', ''),
                slug=form.cleaned_data['title'].lower().replace(' ', '-')[:50]
            )
            
            # Assign uploaded images
            for field_name, image in uploaded_images.items():
                setattr(blog_post, field_name, image)
            
            # Add as child of the blog index page
            parent_page.add_child(instance=blog_post)
            
            # Handle many-to-many relationships
            if form.cleaned_data.get('article_types'):
                blog_post.article_types.set(form.cleaned_data['article_types'])
            if form.cleaned_data.get('locations'):
                blog_post.locations.set(form.cleaned_data['locations'])
            if form.cleaned_data.get('sectors'):
                blog_post.sectors.set(form.cleaned_data['sectors'])
            
            # Publish the page
            blog_post.save_revision().publish()
            
            messages.success(
                request,
                f'Blog post "{blog_post.title}" created successfully!'
            )
            return redirect(parent_page.url)
    else:
        form = BlogPostForm()
    
    context = {
        'form': form,
        'parent_page': parent_page,
    }
    return render(request, 'blog/create_blog_post.html', context)

