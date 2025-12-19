from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, FieldRowPanel
from wagtail.search import index
from wagtail.images import get_image_model
from wagtail import blocks
from wagtail.blocks import CharBlock, TextBlock, StructBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from modelcluster.fields import ParentalManyToManyField
from django.forms import CheckboxSelectMultiple
from django.core.exceptions import ValidationError


class QuoteBlock(StructBlock):
    """
    Custom quote block with person details
    """
    quote = TextBlock(required=True, help_text="Enter the quote text")
    name = CharBlock(required=False, help_text="Person's name")
    job_title = CharBlock(required=False, help_text="Job title")
    company = CharBlock(required=False, help_text="Company name")

    class Meta:
        template = 'blog/blocks/quote_block.html'
        icon = 'openquote'
        label = 'Blockquote'


class ArticleType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Sector(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class BlogIndexPage(Page):
    """
    Main blog index page - lists all blog posts
    """
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request):
        # Update context to include only published posts,
        # ordered by reverse-chron
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at')
        context['blogpages'] = blogpages
        return context


class BlogPage(Page):
    """
    Individual blog post page
    """
    template_name = 'blog/blog-details.html'
    # Basic fields
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = StreamField([
        ('heading', CharBlock(classname="full title", icon="title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('quote', QuoteBlock()),
        ('embed', EmbedBlock()),
        ('document', DocumentChooserBlock()),
    ], blank=True, use_json_field=True)
    
    # Title and header
    title_position = models.CharField(
        max_length=50,
        blank=True,
        help_text="Position of the title"
    )
    page_header = RichTextField(
        blank=True,
        features=[
            'h2', 'h3', 'h4', 'bold', 'italic', 'ol', 'ul', 'link',
            'document-link', 'image', 'embed', 'code', 'blockquote', 'hr'
        ],
        help_text="Optional page header content"
    )
    page_header_image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Choose an image for the page header"
    )
    
    # Thumbnails
    tall_thumbnail = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Tall thumbnail (540px x 750px) - used on Section Page"
    )
    wide_thumbnail = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Wide thumbnail (1140px x 750px) - used on Home Page"
    )
    
    # List options
    featured = models.BooleanField(
        default=False,
        help_text="Feature post (requires tall thumbnail)"
    )
    double_width = models.BooleanField(
        default=False,
        help_text="Double width on home page (requires wide thumbnail)"
    )
    white_text = models.BooleanField(
        default=False,
        help_text="White text for darker images"
    )
    hide_title = models.BooleanField(
        default=False,
        help_text="Hide title when using text in thumbnail"
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        help_text="Color option"
    )
    
    # CM Watermark and media
    cm_watermark = models.BooleanField(
        default=False,
        help_text="CM Watermark?"
    )
    alternative_text = models.CharField(
        max_length=250,
        blank=True,
        help_text="Alternative text"
    )
    icon = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Choose an icon image"
    )
    
    # Categories and tags
    article_types = ParentalManyToManyField(
        'blog.ArticleType',
        blank=True,
        help_text="Select article types"
    )
    locations = ParentalManyToManyField(
        'blog.Location',
        blank=True,
        help_text="Select locations"
    )
    sectors = ParentalManyToManyField(
        'blog.Sector',
        blank=True,
        help_text="Select sectors"
    )
    
    # Social and media
    twitter_body = models.TextField(
        blank=True,
        help_text="Twitter body text"
    )
    vimeo_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Vimeo Video ID"
    )
    
    # Source
    source_link = models.URLField(
        blank=True,
        help_text="Link to the article's source"
    )
    
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
        index.SearchField('page_header'),
        index.SearchField('twitter_body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        MultiFieldPanel([
            FieldPanel('title_position'),
            FieldPanel('page_header'),
            FieldPanel('page_header_image'),
        ], heading="Page Header"),
        MultiFieldPanel([
            FieldPanel('tall_thumbnail'),
            FieldPanel('wide_thumbnail'),
        ], heading="Thumbnails"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('featured'),
                FieldPanel('double_width'),
            ]),
            FieldRowPanel([
                FieldPanel('white_text'),
                FieldPanel('hide_title'),
            ]),
            FieldPanel('color'),
        ], heading="List Options"),
        MultiFieldPanel([
            FieldPanel('cm_watermark'),
            FieldPanel('alternative_text'),
            FieldPanel('icon'),
        ], heading="CM Watermark & Media"),
        MultiFieldPanel([
            FieldPanel('article_types', widget=CheckboxSelectMultiple),
            FieldPanel('locations', widget=CheckboxSelectMultiple),
            FieldPanel('sectors', widget=CheckboxSelectMultiple),
        ], heading="Categories & Tags"),
        MultiFieldPanel([
            FieldPanel('twitter_body'),
            FieldPanel('vimeo_id'),
        ], heading="Social & Media"),
        FieldPanel('body'),
        FieldPanel('source_link'),
    ]


class NewsIndexPage(Page):
    """
    News and Article index page - lists all news articles and key facts
    """
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    subpage_types = ['blog.ArticlePage', 'blog.KeyFactsPage']

    def get_context(self, request):
        # Update context to include only published posts,
        # ordered by reverse-chron
        context = super().get_context(request)
        articles = self.get_children().live().filter(
            content_type__model='articlepage'
        ).order_by('-first_published_at')
        keyfacts = self.get_children().live().filter(
            content_type__model='keyfactspage'
        ).order_by('-first_published_at')
        context['articles'] = articles
        context['keyfacts'] = keyfacts
        return context


class ArticlePage(Page):
    """
    Individual article page - similar to blog post but for news
    """
    template_name = 'blog/blog-details.html'
    # Basic fields
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = StreamField([
        ('heading', CharBlock(classname="full title", icon="title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('quote', QuoteBlock()),
        ('embed', EmbedBlock()),
        ('document', DocumentChooserBlock()),
    ], blank=True, use_json_field=True)
    
    # Title and header
    title_position = models.CharField(
        max_length=50,
        blank=True,
        help_text="Position of the title"
    )
    page_header = RichTextField(
        blank=True,
        features=[
            'h2', 'h3', 'h4', 'bold', 'italic', 'ol', 'ul', 'link',
            'document-link', 'image', 'embed', 'code', 'blockquote', 'hr'
        ],
        help_text="Optional page header content"
    )
    page_header_image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Choose an image for the page header"
    )
    
    # Thumbnails
    tall_thumbnail = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Tall thumbnail (540px x 750px) - used on Section Page"
    )
    wide_thumbnail = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Wide thumbnail (1140px x 750px) - used on Home Page"
    )
    
    # List options
    featured = models.BooleanField(
        default=False,
        help_text="Feature post (requires tall thumbnail)"
    )
    double_width = models.BooleanField(
        default=False,
        help_text="Double width on home page (requires wide thumbnail)"
    )
    white_text = models.BooleanField(
        default=False,
        help_text="White text for darker images"
    )
    hide_title = models.BooleanField(
        default=False,
        help_text="Hide title when using text in thumbnail"
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        help_text="Color option"
    )
    
    # CM Watermark and media
    cm_watermark = models.BooleanField(
        default=False,
        help_text="CM Watermark?"
    )
    alternative_text = models.CharField(
        max_length=250,
        blank=True,
        help_text="Alternative text"
    )
    icon = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Choose an icon image"
    )
    
    # Categories and tags
    article_types = ParentalManyToManyField(
        'blog.ArticleType',
        blank=True,
        help_text="Select article types"
    )
    locations = ParentalManyToManyField(
        'blog.Location',
        blank=True,
        help_text="Select locations"
    )
    sectors = ParentalManyToManyField(
        'blog.Sector',
        blank=True,
        help_text="Select sectors"
    )
    
    # Social and media
    twitter_body = models.TextField(
        blank=True,
        help_text="Twitter body text"
    )
    vimeo_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Vimeo Video ID"
    )
    
    # Source
    source_link = models.URLField(
        blank=True,
        help_text="Link to the article's source"
    )
    
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
        index.SearchField('page_header'),
        index.SearchField('twitter_body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        MultiFieldPanel([
            FieldPanel('title_position'),
            FieldPanel('page_header'),
            FieldPanel('page_header_image'),
        ], heading="Page Header"),
        MultiFieldPanel([
            FieldPanel('tall_thumbnail'),
            FieldPanel('wide_thumbnail'),
        ], heading="Thumbnails"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('featured'),
                FieldPanel('double_width'),
            ]),
            FieldRowPanel([
                FieldPanel('white_text'),
                FieldPanel('hide_title'),
            ]),
            FieldPanel('color'),
        ], heading="List Options"),
        MultiFieldPanel([
            FieldPanel('cm_watermark'),
            FieldPanel('alternative_text'),
            FieldPanel('icon'),
        ], heading="CM Watermark & Media"),
        MultiFieldPanel([
            FieldPanel('article_types', widget=CheckboxSelectMultiple),
            FieldPanel('locations', widget=CheckboxSelectMultiple),
            FieldPanel('sectors', widget=CheckboxSelectMultiple),
        ], heading="Categories & Tags"),
        MultiFieldPanel([
            FieldPanel('twitter_body'),
            FieldPanel('vimeo_id'),
        ], heading="Social & Media"),
        FieldPanel('body'),
        FieldPanel('source_link'),
    ]

    def get_form(self, request, *args, **kwargs):
        """Override form to use checkbox widgets for many-to-many fields"""
        form = super().get_form(request, *args, **kwargs)
        form.fields['article_types'].widget = CheckboxSelectMultiple()
        form.fields['locations'].widget = CheckboxSelectMultiple()
        form.fields['sectors'].widget = CheckboxSelectMultiple()
        return form


class KeyFactsPage(Page):
    """
    Key Facts page - displays important facts and information
    """
    intro = models.CharField(max_length=250, blank=True)
    body = RichTextField(blank=True)
    
    # Header image
    header_image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Choose a header image"
    )
    
    # Key facts (could be a list of facts)
    key_facts = RichTextField(
        blank=True,
        help_text="List of key facts"
    )
    
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
        index.SearchField('key_facts'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('header_image'),
        FieldPanel('body'),
        FieldPanel('key_facts'),
    ]


class SupportPage(Page):
    """
    Support Cash page - promotes cash awareness and provides support resources
    """
    # Page Header
    page_header_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional. Defaults to page title if empty."
    )
    page_header_image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Page Header image"
    )

    # Page Description
    description_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Description title"
    )
    description_image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Choose an image"
    )
    description_content = RichTextField(
        blank=True,
        help_text="Description content"
    )
    description_link = models.URLField(
        blank=True,
        help_text="Optional link for more information."
    )

    # Video Header
    video_file = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="MP4 video file. Add background image for mobile."
    )
    video_background_image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Background image for video section"
    )

    # Introduction
    introduction = RichTextField(
        blank=True,
        help_text="Introduction text"
    )

    # Support Content
    media_contacts = RichTextField(
        blank=True,
        help_text="Media Contacts information"
    )
    members_only = RichTextField(
        blank=True,
        help_text="Members only content"
    )

    search_fields = Page.search_fields + [
        index.SearchField('page_header_title'),
        index.SearchField('description_title'),
        index.SearchField('description_content'),
        index.SearchField('introduction'),
        index.SearchField('media_contacts'),
        index.SearchField('members_only'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('page_header_title'),
            FieldPanel('page_header_image'),
        ], heading="Page Header"),
        MultiFieldPanel([
            FieldPanel('description_title'),
            FieldPanel('description_image'),
            FieldPanel('description_content'),
            FieldPanel('description_link'),
        ], heading="Page Description"),
        MultiFieldPanel([
            FieldPanel('video_file'),
            FieldPanel('video_background_image'),
        ], heading="Video Header"),
        FieldPanel('introduction'),
        MultiFieldPanel([
            FieldPanel('media_contacts'),
            FieldPanel('members_only'),
        ], heading="Support Content"),
    ]

    def clean(self):
        """Ensure only one SupportPage can exist"""
        super().clean()
        
        # Check if another SupportPage already exists
        existing_pages = SupportPage.objects.exclude(pk=self.pk)
        if existing_pages.exists():
            raise ValidationError({
                'title': 'Only one Support page allowed. Edit existing page.'
            })


class FactBlock(StructBlock):
    """
    Individual fact block with reveal functionality
    """
    title = CharBlock(required=True, help_text="Fact title")
    related_sector = CharBlock(required=True, help_text="Related sector")
    background_image = ImageChooserBlock(required=False,
                                         help_text="Background image")
    icon = ImageChooserBlock(required=False, help_text="Icon (234x188 min)")
    color = CharBlock(required=False, help_text="Color theme")
    text = TextBlock(required=True, help_text="Main fact text")
    reveal_title = CharBlock(required=False, help_text="Reveal section title")
    reveal_text = TextBlock(required=False, help_text="Reveal section text")

    class Meta:
        template = 'blog/blocks/fact_block.html'
        icon = 'tick'
        label = 'Fact'


class WhyCashMattersPage(Page):
    """
    Why Cash Matters page - comprehensive guide with interactive facts
    """
    # Basic fields
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = StreamField([
        ('heading', CharBlock(classname="full title", icon="title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('quote', QuoteBlock()),
        ('embed', EmbedBlock()),
        ('document', DocumentChooserBlock()),
    ], blank=True, use_json_field=True)

    # Title and header
    title_position = models.CharField(
        max_length=50,
        blank=True,
        help_text="Position of the title"
    )
    page_header = RichTextField(
        blank=True,
        features=[
            'h2', 'h3', 'h4', 'bold', 'italic', 'ol', 'ul', 'link',
            'document-link', 'image', 'embed', 'code', 'blockquote', 'hr'
        ],
        help_text="Optional page header content"
    )
    page_header_image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Choose an image for the page header"
    )

    # Thumbnails
    tall_thumbnail = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Tall thumbnail (540px x 750px) - used on Section Page"
    )
    wide_thumbnail = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Wide thumbnail (1140px x 750px) - used on Home Page"
    )

    # List options
    featured = models.BooleanField(
        default=False,
        help_text="Feature post (requires tall thumbnail)"
    )
    double_width = models.BooleanField(
        default=False,
        help_text="Double width on home page (requires wide thumbnail)"
    )
    white_text = models.BooleanField(
        default=False,
        help_text="White text for darker images"
    )
    hide_title = models.BooleanField(
        default=False,
        help_text="Hide title when using text in thumbnail"
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        help_text="Color option"
    )

    # CM Watermark and media
    cm_watermark = models.BooleanField(
        default=False,
        help_text="CM Watermark?"
    )
    alternative_text = models.CharField(
        max_length=250,
        blank=True,
        help_text="Alternative text"
    )
    icon = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Choose an icon image"
    )

    # Categories and tags
    article_types = ParentalManyToManyField(
        'blog.ArticleType',
        blank=True,
        help_text="Select article types"
    )
    locations = ParentalManyToManyField(
        'blog.Location',
        blank=True,
        help_text="Select locations"
    )
    sectors = ParentalManyToManyField(
        'blog.Sector',
        blank=True,
        help_text="Select sectors"
    )

    # Social and media
    twitter_body = models.TextField(
        blank=True,
        help_text="Twitter body text"
    )
    vimeo_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Vimeo Video ID"
    )

    # Source
    source_link = models.URLField(
        blank=True,
        help_text="Link to the article's source"
    )

    # Facts section
    facts = StreamField([
        ('fact', FactBlock()),
    ], blank=True, use_json_field=True,
       help_text="Add facts with reveal functionality")

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
        index.SearchField('page_header'),
        index.SearchField('twitter_body'),
        index.SearchField('facts'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        MultiFieldPanel([
            FieldPanel('title_position'),
            FieldPanel('page_header'),
            FieldPanel('page_header_image'),
        ], heading="Page Header"),
        MultiFieldPanel([
            FieldPanel('tall_thumbnail'),
            FieldPanel('wide_thumbnail'),
        ], heading="Thumbnails"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('featured'),
                FieldPanel('double_width'),
            ]),
            FieldRowPanel([
                FieldPanel('white_text'),
                FieldPanel('hide_title'),
            ]),
            FieldPanel('color'),
        ], heading="List Options"),
        MultiFieldPanel([
            FieldPanel('cm_watermark'),
            FieldPanel('alternative_text'),
            FieldPanel('icon'),
        ], heading="CM Watermark & Media"),
        MultiFieldPanel([
            FieldPanel('article_types', widget=CheckboxSelectMultiple),
            FieldPanel('locations', widget=CheckboxSelectMultiple),
            FieldPanel('sectors', widget=CheckboxSelectMultiple),
        ], heading="Categories & Tags"),
        MultiFieldPanel([
            FieldPanel('twitter_body'),
            FieldPanel('vimeo_id'),
        ], heading="Social & Media"),
        FieldPanel('body'),
        FieldPanel('facts'),
        FieldPanel('source_link'),
    ]

    def clean(self):
        """Ensure only one WhyCashMattersPage can exist"""
        super().clean()
        
        # Check if another WhyCashMattersPage already exists
        existing_pages = WhyCashMattersPage.objects.exclude(pk=self.pk)
        if existing_pages.exists():
            raise ValidationError({
                'title': 'Only one Why Cash Matters page allowed.'
            })

    def get_form(self, request, *args, **kwargs):
        """Override form to use checkbox widgets for many-to-many fields"""
        form = super().get_form(request, *args, **kwargs)
        form.fields['article_types'].widget = CheckboxSelectMultiple()
        form.fields['locations'].widget = CheckboxSelectMultiple()
        form.fields['sectors'].widget = CheckboxSelectMultiple()
        return form
