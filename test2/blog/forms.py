from django import forms
from .models import BlogPage
import json
from django.utils.safestring import mark_safe


class ContentBlockWidget(forms.Widget):
    """Custom widget for content blocks"""
    
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        elif isinstance(value, str):
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                value = []
        
        html = '<div id="content-blocks" class="content-blocks-container">'
        html += '<div class="content-blocks-toolbar">'
        html += '<button type="button" class="add-block-btn" '
        html += 'data-block-type="content">📝 Content</button>'
        html += '<button type="button" class="add-block-btn" '
        html += 'data-block-type="image_caption">🖼️ Image & Caption</button>'
        html += '<button type="button" class="add-block-btn" '
        html += 'data-block-type="video_caption">🎥 Video & Caption</button>'
        html += '<button type="button" class="add-block-btn" '
        html += 'data-block-type="iframe_caption">🔗 Iframe & Caption</button>'
        html += '<button type="button" class="add-block-btn" '
        html += 'data-block-type="blockquote">💬 Blockquote</button>'
        html += '<button type="button" class="add-block-btn" '
        html += 'data-block-type="data_table">📊 Data Table</button>'
        html += '<button type="button" class="add-block-btn" '
        html += 'data-block-type="poll">📊 Poll</button>'
        html += '<button type="button" class="add-block-btn" '
        html += 'data-block-type="facts_carousel">🎠 Facts Carousel</button>'
        html += '<button type="button" class="add-block-btn" '
        html += 'data-block-type="key_fact_image">🔑 Key Fact Image</button>'
        html += '</div>'
        html += '<div class="content-blocks-list">'
        
        for i, block in enumerate(value):
            html += self.render_block(block, i, name)
        
        html += '</div>'
        html += '<input type="hidden" name="{}" id="id_{}" '.format(name, name)
        html += 'value=\'{}\'>'.format(json.dumps(value))
        html += '</div>'
        return mark_safe(html)
    
    def render_block(self, block, index, field_name):
        block_type = block.get('type', 'content')
        html = '<div class="content-block" data-block-type="{}" '.format(
            block_type)
        html += 'data-block-index="{}">'.format(index)
        html += '<div class="block-header">'
        html += '<span class="block-type">{}</span>'.format(
            block_type.replace("_", " ").title())
        html += '<button type="button" class="remove-block-btn">✕</button>'
        html += '</div>'
        html += '<div class="block-content">'
        
        if block_type == 'content':
            html += '<textarea name="block_{}_content" '.format(index)
            html += 'placeholder="Enter your content here..." rows="6">'
            html += '{}</textarea>'.format(block.get("content", ""))
        elif block_type == 'image_caption':
            html += '<div class="image-upload-group">'
            html += '<input type="file" name="block_{}_image" '.format(index)
            html += 'accept="image/*">'
            html += '<input type="text" name="block_{}_caption" '.format(index)
            html += 'placeholder="Image caption" value="{}">'.format(
                block.get("caption", ""))
            html += '</div>'
        elif block_type == 'video_caption':
            html += '<div class="video-upload-group">'
            html += '<input type="file" name="block_{}_video" '.format(index)
            html += 'accept="video/*">'
            html += '<input type="text" name="block_{}_caption" '.format(index)
            html += 'placeholder="Video caption" value="{}">'.format(
                block.get("caption", ""))
            html += '</div>'
        elif block_type == 'iframe_caption':
            html += '<div class="iframe-group">'
            html += '<input type="url" name="block_{}_url" '.format(index)
            html += 'placeholder="Iframe URL" value="{}">'.format(
                block.get("url", ""))
            html += '<input type="text" name="block_{}_caption" '.format(index)
            html += 'placeholder="Iframe caption" value="{}">'.format(
                block.get("caption", ""))
            html += '</div>'
        elif block_type == 'blockquote':
            html += '<textarea name="block_{}_quote" '.format(index)
            html += 'placeholder="Enter blockquote text..." rows="4">'
            html += '{}</textarea>'.format(block.get("quote", ""))
            html += '<input type="text" name="block_{}_author" '.format(index)
            html += 'placeholder="Author (optional)" value="{}">'.format(
                block.get("author", ""))
        elif block_type == 'data_table':
            html += '<textarea name="block_{}_table_data" '.format(index)
            html += 'placeholder="Enter table data..." rows="8">'
            html += '{}</textarea>'.format(block.get("table_data", ""))
        elif block_type == 'poll':
            html += '<input type="text" name="block_{}_question"'.format(
                index)
            html += ' placeholder="Poll question" value="{}">'.format(
                block.get("question", ""))
            html += '<textarea name="block_{}_options" '.format(index)
            html += 'placeholder="Poll options (one per line)" rows="4">'
            html += '{}</textarea>'.format(block.get("options", ""))
        elif block_type == 'facts_carousel':
            html += '<textarea name="block_{}_facts" '.format(index)
            html += 'placeholder="Enter facts as JSON array..." rows="6">'
            html += '{}</textarea>'.format(block.get("facts", ""))
        elif block_type == 'key_fact_image':
            html += '<div class="key-fact-group">'
            html += '<input type="text" name="block_{}_fact" '.format(index)
            html += 'placeholder="Key fact text" value="{}">'.format(
                block.get("fact", ""))
            html += '<input type="file" name="block_{}_image" '.format(index)
            html += 'accept="image/*">'
            html += '</div>'
        
        html += '</div></div>'
        return html


class ContentBlockField(forms.Field):
    """Custom field for content blocks"""
    widget = ContentBlockWidget
    
    def to_python(self, value):
        if value is None or value == '':
            return []
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return []
        return value
    
    def validate(self, value):
        super().validate(value)
        # Add custom validation if needed


class BlogPostForm(forms.ModelForm):
    """Form for creating blog posts from the frontend"""
    
    # Custom image upload fields for frontend
    tall_thumbnail_upload = forms.ImageField(
        required=False,
        help_text="Upload a tall thumbnail image (540px x 750px)"
    )
    wide_thumbnail_upload = forms.ImageField(
        required=False,
        help_text="Upload a wide thumbnail image (1140px x 750px)"
    )
    page_header_image_upload = forms.ImageField(
        required=False,
        help_text="Upload a page header image"
    )
    icon_upload = forms.ImageField(
        required=False,
        help_text="Upload an icon image"
    )
    
    # Color choices for the color field
    COLOR_CHOICES = [
        ('', '---------'),
        ('#a43245', 'Red'),
        ('#b94012', 'Orange'),
        ('#edd847', 'Yellow'),
        ('#b7bd07', 'Green'),
        ('#008c86', 'Teal'),
        ('#23b0e6', 'Blue'),
        ('#daadd0', 'Purple'),
        ('#957a45', 'Sand'),
    ]
    
    color = forms.ChoiceField(
        choices=COLOR_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Content blocks field instead of simple body
    content_blocks = ContentBlockField(required=False)
    
    class Meta:
        model = BlogPage
        fields = [
            'title', 'date', 'intro',
            'title_position', 'page_header',
            'featured', 'double_width', 'white_text', 'hide_title', 'color',
            'cm_watermark', 'alternative_text',
            'article_types', 'locations', 'sectors',
            'twitter_body', 'vimeo_id', 'source_link'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter blog title'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'intro': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Short introduction',
                'rows': 3
            }),
            'title_position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Title position'
            }),
            'page_header': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Page header content',
                'rows': 4
            }),
            'alternative_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alternative text'
            }),
            'twitter_body': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Twitter body text',
                'rows': 3
            }),
            'vimeo_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Vimeo Video ID'
            }),
            'source_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://...'
            }),
            'article_types': forms.CheckboxSelectMultiple(),
            'locations': forms.CheckboxSelectMultiple(),
            'sectors': forms.CheckboxSelectMultiple(),
        }
