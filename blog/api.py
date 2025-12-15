from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet
from wagtail.api.v2.filters import (
    FieldsFilter,
    OrderingFilter,
    SearchFilter,
)

from .models import ArticlePage

# Create the router. "wagtailapi" is the URL namespace
api_router = WagtailAPIRouter('wagtailapi')

# Create a custom Pages API endpoint for blog posts
class BlogPagesAPIViewSet(PagesAPIViewSet):
    model = ArticlePage

    # Configure the fields that should be returned in the API response
    body_fields = [
        'title',
        'date',
        'intro',
        'body',
        'title_position',
        'page_header',
        'featured',
        'double_width',
        'white_text',
        'hide_title',
        'color',
        'cm_watermark',
        'alternative_text',
        'article_types',
        'locations',
        'sectors',
        'twitter_body',
        'vimeo_id',
        'source_link',
        'tall_thumbnail',
        'wide_thumbnail',
        'page_header_image',
        'icon',
    ]

    # Configure meta fields
    meta_fields = [
        'type',
        'detail_url',
        'html_url',
        'slug',
        'first_published_at',
        'last_published_at',
        'locale',
    ]

    # Configure filters
    filter_backends = [
        FieldsFilter,
        OrderingFilter,
        SearchFilter,
    ]

    # Configure ordering
    ordering_fields = [
        'title',
        'date',
        'first_published_at',
        'last_published_at',
    ]

    # Configure search fields
    search_fields = [
        'title',
        'intro',
        'body',
    ]

    # Override get_queryset to return all blog pages, not just site descendants
    def get_queryset(self):
        return ArticlePage.objects.live().order_by('-first_published_at')

# Register the custom endpoint
api_router.register_endpoint('blog', BlogPagesAPIViewSet)

# Add the standard endpoints
api_router.register_endpoint('pages', PagesAPIViewSet)
api_router.register_endpoint('images', ImagesAPIViewSet)
api_router.register_endpoint('documents', DocumentsAPIViewSet)