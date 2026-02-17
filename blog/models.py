from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, FieldRowPanel
from wagtail.search import index
from wagtail.images import get_image_model
from wagtail import blocks
from wagtail.blocks import CharBlock, TextBlock, RichTextBlock, StructBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from modelcluster.fields import ParentalManyToManyField
from django.forms import CheckboxSelectMultiple
from django.core.exceptions import ValidationError
from wagtail.models import Page
from .mixins import OpenGraphMixin


# blog/blocks.py  (կամ models.py-ի վերևում)

# blog/blocks.py

from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from wagtail.blocks import PageChooserBlock

# ✅ TableBlock (real table UI in admin)
from wagtail.contrib.table_block.blocks import TableBlock

# ✅ Poll chooser (if Poll is a Snippet)
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.snippets.models import register_snippet


# ---------------------------
# Content *
# ---------------------------

class ImageCaptionBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)

    caption = blocks.CharBlock(required=False)

    align_caption_bottom = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Align caption with bottom of image?"
    )

    internal_link = PageChooserBlock(
        required=False,
        help_text="Choose a page"
    )

    external_link = blocks.URLBlock(
        required=False,
        help_text="External link"
    )

    class Meta:
        icon = "image"
        label = "Image & Caption"

class ContentBlock(blocks.StructBlock):
    content = blocks.RichTextBlock(required=True)

    class Meta:
        icon = "doc-full"
        label = "Content"


class VideoCaptionBlock(blocks.StructBlock):
    video_url = EmbedBlock(
        required=True,
        help_text="Paste YouTube or Vimeo URL"
    )

    caption = blocks.CharBlock(required=False)

    align_caption_bottom = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Align caption with bottom of video?"
    )

    internal_link = PageChooserBlock(
        required=False,
        help_text="Choose a page"
    )

    external_link = blocks.URLBlock(
        required=False,
        help_text="External link"
    )

    class Meta:
        icon = "media"
        label = "Video & Caption"



# ---------------------------
# Data Table
# Title, Table*, Table headers, Table caption
# ---------------------------
class DataTableBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    table = TableBlock(required=True)

    # Header option (like Wagtail TableBlock UI)
    TABLE_HEADER_CHOICES = [
        ("none", "No headers"),
        ("row", "First row"),
        ("column", "First column"),
        ("both", "First row and first column"),
    ]
    table_headers = blocks.ChoiceBlock(
        choices=TABLE_HEADER_CHOICES,
        required=False,
        default="row",
        help_text="Which cells should be displayed as headers?"
    )

    table_caption = blocks.CharBlock(
        required=False,
        help_text="A heading that identifies the overall topic of the table, useful for screen reader users."
    )

    class Meta:
        icon = "table"
        label = "Data Table"


# ---------------------------
# Poll (Choose Poll)
# Assume you have Poll as Snippet model: blog.Poll
# ---------------------------
class PollBlock(blocks.StructBlock):
    poll = SnippetChooserBlock(
        target_model="blog.Poll",
        required=True,
        help_text="Choose Poll"
    )

    class Meta:
        icon = "form"
        label = "Poll"


# ---------------------------
# Key Fact Image
# Choose a page (Blog Page - Key Fact)
# -> you have KeyFactsPage model already
# ---------------------------
class KeyFactImageBlock(blocks.StructBlock):
    key_fact_page = PageChooserBlock(
        page_type=["blog.KeyFactsPage"],
        required=True,
        help_text='Choose a page (Blog Page - Key Facts)'
    )

    class Meta:
        icon = "pick"
        label = "Key Facts Image"


# ---------------------------
# Iframe & Caption
# ---------------------------
class IframeCaptionBlock(blocks.StructBlock):
    iframe_url = blocks.URLBlock(required=True)
    iframe_height = blocks.IntegerBlock(required=True, default=480)
    caption = blocks.CharBlock(required=False)
    align_caption_bottom = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Align caption with bottom of iframe?"
    )

    class Meta:
        icon = "code"
        label = "Iframe & Caption"


# ---------------------------
# Facts Carousel
# Slides: list of pages (BlogPage)
# ---------------------------
class FactsCarouselBlock(blocks.StructBlock):
    slides = blocks.ListBlock(
        PageChooserBlock(page_type=["blog.BlogPage"]),
        required=True
    )

    class Meta:
        icon = "list-ul"   # ← փոխեցինք
        label = "Facts Carousel"


# ---------------------------
# Blockquote
# Name, Job title, Company, Quote text*
# ---------------------------
class BlockquoteBlock(blocks.StructBlock):
    name = blocks.CharBlock(required=False)
    job_title = blocks.CharBlock(required=False)
    company = blocks.CharBlock(required=False)
    quote_text = blocks.TextBlock(required=True)

    class Meta:
        icon = "openquote"
        label = "Blockquote"



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


class Author(models.Model):
    """Author snippet model for managing content creators"""
    name = models.CharField(max_length=100, unique=True, help_text="Author's full name")
    job_title = models.CharField(max_length=200, blank=True, help_text="Author's job title or role")
    profile_image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Author's profile picture"
    )
    bio = models.TextField(blank=True, help_text="Short biography of the author")
    email = models.EmailField(blank=True, help_text="Author's email address")
    linkedin_url = models.URLField(blank=True, help_text="LinkedIn profile URL")
    twitter_url = models.URLField(blank=True, help_text="Twitter/X profile URL")

    panels = [
        FieldPanel('name'),
        FieldPanel('job_title'),
        FieldPanel('profile_image'),
        FieldPanel('bio'),
        MultiFieldPanel([
            FieldPanel('email'),
            FieldPanel('linkedin_url'),
            FieldPanel('twitter_url'),
        ], heading="Contact & Social"),
    ]

    def __str__(self):
        return self.name

    def get_article_count(self):
        """Return the total count of articles by this author"""
        from django.db.models import Q
        blog_count = BlogPage.objects.filter(author_profile=self).count()
        article_count = ArticlePage.objects.filter(author_profile=self).count()
        return blog_count + article_count

    class Meta:
        ordering = ['name']





class BlogIndexPage(Page):
    """
    Main blog index page - lists all blog posts
    """
    template = "blog/blog_index_page.html"
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


class BlogPage(OpenGraphMixin, Page):
    """
    Individual blog post page
    """
    template = "blog/blog_page.html"
    # Basic fields
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)

    # Author profile - link to Author snippet
    author_profile = models.ForeignKey(
        'blog.Author',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='blog_posts',
        help_text="Select an author from the Author database"
    )

    # Legacy author fields (for backwards compatibility)
    author = models.CharField(max_length=100, blank=True, help_text="Author name (legacy - use Author Profile instead)")
    author_image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Author profile picture (legacy - use Author Profile instead)"
    )
    body = StreamField([
        ("content", ContentBlock()),
        ("image_caption", ImageCaptionBlock()),
        ("video_caption", VideoCaptionBlock()),
        ("iframe_caption", IframeCaptionBlock()),
        ("blockquote", BlockquoteBlock()),
        ("data_table", DataTableBlock()),
        ("poll", PollBlock()),
        ("facts_carousel", FactsCarouselBlock()),
        ("key_fact_image", KeyFactImageBlock()),
    ], blank=True, use_json_field=True)
    
    # Title and header
    title_position = models.CharField(
        max_length=50,
        blank=True,
        help_text="Position of the title"
    )
    page_header = RichTextField(
        verbose_name="Title",
        blank=True,
        features=[
            'h2', 'h3', 'h4', 'bold', 'italic', 'ol', 'ul', 'link',
            'document-link', 'image', 'embed', 'code', 'blockquote', 'hr'
        ],
        help_text="Optional. If nothing is entered, the page title will be used."
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

    editors_pick = models.BooleanField(default=False, help_text="Feature this post in the Editor’s Pick section.")
    cover_story = models.BooleanField(default=False, help_text="Display this post as a main cover story.")

    featured = models.BooleanField(
        default=False,
        help_text="To feature a post, ensure it has tall thumbnail."
    )
    double_width = models.BooleanField(
        default=False,
        help_text="Make a thumbnail double width on the home page. Must have a wide thumbnail."
    )
    white_text = models.BooleanField(
        default=False,
        help_text="Toggle the icons and text to white, perfect for darker images."
    )
    hide_title = models.BooleanField(
        default=False,
        help_text="Hide the post title when you're using text within your thumbnail."
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        help_text="Color option"
    )
    
    # CM Watermark and media
    cm_watermark = models.BooleanField(
        "CM Watermark",
        default=False,
        help_text="CM Watermark?"
    )
    alternative_text = models.CharField(
        "Alternative Text",
        max_length=250,
        blank=True,
        help_text="Alternative Text"
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
        "Vimeo ID",
        max_length=50,
        blank=True,
        help_text="The Vimeo Video ID (the number at the end of the video url)"
    )

    # Source
    source_link = models.URLField(
        "Source Link",
        blank=True,
        help_text="Link to the article's source, if any."
    )

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
        index.SearchField('page_header'),
        index.SearchField('twitter_body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('author_profile'),
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
                FieldPanel('editors_pick'),
                FieldPanel('cover_story'),
            ]),
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

    promote_panels = Page.promote_panels + OpenGraphMixin.og_panels




class NewsIndexPage(Page):
    """
    News and Article index page - lists all news articles and key facts
    """
    template = "blog/news_index_page.html"
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


class ArticlePage(OpenGraphMixin, Page):
    """
    Individual article page - similar to blog post but for news
    """
    template = 'blog/blog-details.html'
    # Basic fields
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)

    # Author profile - link to Author snippet
    author_profile = models.ForeignKey(
        'blog.Author',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='articles',
        help_text="Select an author from the Author database"
    )

    # Legacy author fields (for backwards compatibility)
    author = models.CharField(max_length=100, blank=True, help_text="Author name (legacy - use Author Profile instead)")
    author_image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Author profile picture (legacy - use Author Profile instead)"
    )
    body = StreamField([
        ("content", ContentBlock()),
        ("data_table", DataTableBlock()),
        ("poll", PollBlock()),
        ("facts_carousel", FactsCarouselBlock()),
        ("key_fact_image", KeyFactImageBlock()),
        ("iframe_caption", IframeCaptionBlock()),
        ("blockquote", BlockquoteBlock()),
    ], blank=True, use_json_field=True)
    
    # Title and header
    title_position = models.CharField(
        max_length=50,
        blank=True,
        help_text="Position of the title"
    )
    page_header = RichTextField(
        verbose_name="Page Header",
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

    editors_pick = models.BooleanField(default=False, help_text="Feature this post in the Editor’s Pick section.")
    cover_story = models.BooleanField(default=False, help_text="Display this post as a main cover story.")


    featured = models.BooleanField(
        default=False,
        help_text="To feature a post, ensure it has tall thumbnail."
    )

    double_width = models.BooleanField(
        default=False,
        help_text="Make a thumbnail double width on the home page. Must have a wide thumbnail."
    )
    white_text = models.BooleanField(
        default=False,
        help_text="Toggle the icons and text to white, perfect for darker images."
    )
    hide_title = models.BooleanField(
        default=False,
        help_text="Hide the post title when you're using text within your thumbnail."
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        help_text="Color option"
    )
    
    # CM Watermark and media
    cm_watermark = models.BooleanField(
        "CM Watermark",
        default=False,
        help_text="CM Watermark?"
    )
    alternative_text = models.CharField(
        "Alternative Text",
        max_length=250,
        blank=True,
        help_text="Alternative Text"
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
        "Vimeo ID",
        max_length=50,
        blank=True,
        help_text="The Vimeo Video ID (the number at the end of the video url)",

    )

    # Source
    source_link = models.URLField(
        "Source Link",
        blank=True,
        help_text="Link to the article's source, if any."
    )

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
        index.SearchField('page_header'),
        index.SearchField('twitter_body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('author_profile'),
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
            FieldRowPanel([FieldPanel('editors_pick'), FieldPanel('cover_story')]),

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

    promote_panels = Page.promote_panels + OpenGraphMixin.og_panels

    def get_form(self, request, *args, **kwargs):
        """Override form to use checkbox widgets for many-to-many fields"""
        form = super().get_form(request, *args, **kwargs)
        form.fields['article_types'].widget = CheckboxSelectMultiple()
        form.fields['locations'].widget = CheckboxSelectMultiple()
        form.fields['sectors'].widget = CheckboxSelectMultiple()
        return form


class KeyFactsPage(Page):
    template = "blog/key_facts_page.html"

    # --- OLD FIELDS (keep) ---
    intro = models.CharField(max_length=250, blank=True)
    body = models.TextField(blank=True)  # keep, do NOT convert
    header_image = models.ForeignKey(
        get_image_model(), null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )
    key_facts = models.TextField(blank=True)

    # ✅ NEW BODY (StreamField) - safe approach
    body_blocks = StreamField([
        ("content", ContentBlock()),
        ("data_table", DataTableBlock()),
        ("poll", PollBlock()),
        ("facts_carousel", FactsCarouselBlock()),
        ("key_fact_image", KeyFactImageBlock()),
        ("iframe_caption", IframeCaptionBlock()),
        ("blockquote", BlockquoteBlock()),
    ], blank=True, use_json_field=True)

    # --- OLD backend like fields ---
    page_header_title = models.CharField(
        max_length=255, blank=True,
        help_text="Optional. If nothing is entered, the page title will be used."
    )
    page_header_image = models.ForeignKey(
        get_image_model(), null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
        help_text="Choose an image"
    )

    date = models.DateField("Post date", null=True, blank=True)

    double_width = models.BooleanField(
        default=False,
        help_text="Make a thumbnail double width on the home page. Must have a wide thumbnail."
    )
    color = models.CharField(max_length=50, blank=True)

    featured_data = models.CharField(
        max_length=50, blank=True,
        help_text="This is the large featured number used on key fact cards"
    )
    featured_data_color = models.CharField(
        max_length=50, blank=True,
        help_text="The color for the feature. White will be used if not selected"
    )

    alternative_text = models.CharField(max_length=250, blank=True)
    fact_source = models.CharField(max_length=255, blank=True, help_text="The cited source for the fact")
    source_link = models.URLField("Source Link", blank=True, help_text="Link to the article's source, if any.")

    twitter_body = models.TextField(blank=True)
    vimeo_id = models.CharField(
        max_length=50, blank=True,
        help_text="The Vimeo Video ID (the number at the end of the video url)"
    )

    # ✅ ONLY allowed categories & tags (ArticleType)
    article_types = ParentalManyToManyField(
        "blog.ArticleType",
        blank=True,
        help_text="Select article types"
    )

    content_panels = Page.content_panels + [
        FieldPanel("featured_data"),
        FieldPanel("featured_data_color"),
        FieldPanel("intro"),
        FieldPanel("page_header_image"),
        FieldPanel("alternative_text"),
        FieldPanel("date"),
    ]


class SupportPage(Page):
    """
    Support Cash page - promotes cash awareness and provides support resources
    """
    template = "support.html"
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
        
        # Check if another SupportPage already exists by content type
        from django.contrib.contenttypes.models import ContentType
        support_ct = ContentType.objects.get_for_model(SupportPage)
        existing_pages = Page.objects.filter(
            content_type=support_ct
        ).exclude(pk=self.pk)
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


class FeatureCardBlock(StructBlock):
    """
    Feature card block with icon and content sections
    """
    # Icon card fields
    icon_title = CharBlock(required=True, help_text="Title for the icon card")
    icon = CharBlock(required=False,
                     help_text="Bootstrap icon class (e.g., bi-send)")
    color = CharBlock(required=False, choices=[
        ('blue', 'Blue'),
        ('red', 'Red'),
        ('purple', 'Purple'),
        ('orange', 'Orange'),
    ], default='blue', help_text="Color theme for the icon card")

    # Content card fields
    content_title = CharBlock(required=True,
                              help_text="Main heading for content card")
    content_text = TextBlock(required=True, help_text="Description text")
    background_image = ImageChooserBlock(required=False,
                                         help_text="Background image")

    class Meta:
        template = 'blog/blocks/feature_card_block.html'
        icon = 'doc-full'
        label = 'Feature Card'


class WhyCashMattersPage(Page):
    """
    Why Cash Matters page - comprehensive guide with interactive facts
    """
    template = "why-cash.html"
    # Basic fields
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = StreamField([
        ("content", ContentBlock()),
        ("data_table", DataTableBlock()),
        ("poll", PollBlock()),
        ("facts_carousel", FactsCarouselBlock()),
        ("key_fact_image", KeyFactImageBlock()),
        ("iframe_caption", IframeCaptionBlock()),
        ("blockquote", BlockquoteBlock()),
    ], blank=True, use_json_field=True)

    # Title and header
    title_position = models.CharField(
        max_length=50,
        blank=True,
        help_text="Position of the title"
    )
    page_header = RichTextField(
        verbose_name="Page Header",
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
        help_text="To feature a post, ensure it has tall thumbnail."
    )
    double_width = models.BooleanField(
        default=False,
        help_text="Make a thumbnail double width on the home page. Must have a wide thumbnail."
    )
    white_text = models.BooleanField(
        default=False,
        help_text="Toggle the icons and text to white, perfect for darker images."
    )
    hide_title = models.BooleanField(
        default=False,
        help_text="Hide the post title when you're using text within your thumbnail."
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        help_text="Color option"
    )

    # CM Watermark and media
    cm_watermark = models.BooleanField(
        "CM Watermark",
        default=False,
        help_text="CM Watermark?"
    )
    alternative_text = models.CharField(
        "Alternative Text",
        max_length=250,
        blank=True,
        help_text="Alternative Text"
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
        "Vimeo ID",
        max_length=50,
        blank=True,
        help_text="The Vimeo Video ID (the number at the end of the video url)"
    )

    # Source
    source_link = models.URLField(
        "Source Link",
        blank=True,
        help_text="Link to the article's source, if any."
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
        index.SearchField('facts')
        ,
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
        
        # Check if another WhyCashMattersPage already exists by content type
        from django.contrib.contenttypes.models import ContentType
        whycash_ct = ContentType.objects.get_for_model(WhyCashMattersPage)
        existing_pages = Page.objects.filter(
            content_type=whycash_ct
        ).exclude(pk=self.pk)
        if existing_pages.exists():
            raise ValidationError({
                'title': 'Only one Why Cash Matters page allowed.'
            })

    def get_form(self, request, *args, **kwargs):
        """Override form to use checkbox widgets for many-to-many fields"""
        form = super().get_form(request, *args, **kwargs)
        form.fields['article_types'].widget = CheckboxSelectMultiple()
        return form


class WhyCashFeatureCardBlock(StructBlock):
    """
    Individual feature card for Why Cash Matters Feature Page
    """
    title = CharBlock(required=True, help_text="Card title")
    description = RichTextBlock(
        required=True,
        help_text="Card description (supports links and formatting)"
    )
    icon_type = CharBlock(
        required=False,
        help_text="Icon type: svg, emoji, or image"
    )
    icon_svg_code = TextBlock(
        required=False,
        help_text="SVG code for the icon (if icon_type is svg)"
    )
    icon_emoji = CharBlock(
        required=False,
        max_length=10,
        help_text="Emoji character (if icon_type is emoji)"
    )
    icon_image = ImageChooserBlock(
        required=False,
        help_text="Upload icon image (if icon_type is image)"
    )
    modal_image = ImageChooserBlock(
        required=False,
        help_text="Background image for modal popup (optional)"
    )
    color = CharBlock(
        required=False,
        choices=[
            ('blue', 'Blue'),
            ('red', 'Red'),
            ('gold', 'Gold'),
            ('green', 'Green'),
        ],
        default='blue',
        help_text="Icon color theme"
    )
    card_size = CharBlock(
        required=False,
        choices=[
            ('large', 'Large (Top Featured)'),
            ('small', 'Small (Bottom Grid)'),
        ],
        default='small',
        help_text="Card size"
    )

    class Meta:
        template = 'blog/blocks/why_cash_feature_card.html'
        icon = 'form'
        label = 'Feature Card'


class WhyCashMattersFeaturePage(Page):
    """
    Dynamic Why Cash Matters Feature Page with editable cards
    """
    template = "new_page.html"
    max_count = 1  # Only allow one instance
    
    # Page header
    page_title = models.CharField(
        max_length=255,
        default="Why Cash Matters",
        help_text="Main page title"
    )
    page_date = models.CharField(
        max_length=100,
        blank=True,
        default="Apr 1, 2025",
        help_text="Display date"
    )
    intro_text = models.TextField(
        help_text="Introduction paragraph"
    )
    
    # Feature cards
    feature_cards = StreamField([
        ('card', WhyCashFeatureCardBlock()),
    ], blank=True, use_json_field=True,
       help_text="Add feature cards (first 2 will be large, rest will be in bottom grid)")

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('page_title'),
            FieldPanel('page_date'),
            FieldPanel('intro_text'),
        ], heading="Page Header"),
        FieldPanel('feature_cards'),
    ]

    def clean(self):
        """Ensure only one WhyCashMattersFeaturePage can exist"""
        super().clean()
        
        from django.contrib.contenttypes.models import ContentType
        feature_ct = ContentType.objects.get_for_model(WhyCashMattersFeaturePage)
        existing_pages = Page.objects.filter(
            content_type=feature_ct
        ).exclude(pk=self.pk)
        if existing_pages.exists():
            raise ValidationError({
                'title': 'Only one Why Cash Matters Feature page allowed.'
            })


from django.db import models

from django.db import models
from django.db.models import F

from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.models import Orderable


@register_snippet
class Poll(ClusterableModel):
    title = models.CharField(max_length=255)

    results_title = models.CharField(max_length=255, blank=True)
    results_content = RichTextField(blank=True)

    is_global = models.BooleanField(default=False)

    panels = [
        FieldPanel("title"),
        FieldPanel("results_title"),
        FieldPanel("results_content"),
        FieldPanel("is_global"),
        InlinePanel("choices", label="Choice"),
    ]

    def __str__(self):
        return self.title


class PollChoice(Orderable):
    poll = ParentalKey("blog.Poll", on_delete=models.CASCADE, related_name="choices")

    # ✅ old backend-ում սա կոչվում է "Question"
    question = models.CharField(max_length=255)

    # ✅ votes default 0
    votes = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("question"),
        FieldPanel("votes"),  # եթե ուզում ես երևա admin-ում
    ]

    def __str__(self):
        return self.question


from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel

@register_snippet
class ArticleType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    panels = [FieldPanel("name")]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

@register_snippet
class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    panels = [FieldPanel("name")]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

from django.utils.text import slugify

@register_snippet
class Sector(models.Model):
    name = models.CharField(max_length=100, unique=True)

    slug = models.SlugField(
        max_length=120,
        unique=True,
        null=True,      # 👈 կարևոր
        blank=True,
        help_text="Auto-generated from name if left blank"
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]




from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel


@register_snippet
class BrandAssetTag(models.Model):
    title = models.CharField(max_length=100)

    tag_colour = models.CharField(
        max_length=20,
        blank=True,
        help_text="Optional: Tag will appear grey if a colour is not chosen."
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("tag_colour"),
    ]

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]
