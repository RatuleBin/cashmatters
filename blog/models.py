from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, FieldRowPanel
from wagtail.search import index
from wagtail.images import get_image_model
from modelcluster.fields import ParentalManyToManyField
from django.forms import CheckboxSelectMultiple


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
    # Basic fields
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    
    # Title and header
    title_position = models.CharField(
        max_length=50,
        blank=True,
        help_text="Position of the title"
    )
    page_header = RichTextField(
        blank=True,
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
    # Basic fields
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    
    # Title and header
    title_position = models.CharField(
        max_length=50,
        blank=True,
        help_text="Position of the title"
    )
    page_header = RichTextField(
        blank=True,
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
