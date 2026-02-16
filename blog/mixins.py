# blog/mixins.py
from django.db import models
from wagtail.images import get_image_model
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

class OpenGraphMixin(models.Model):
    og_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Open Graph title (social share title)"
    )
    og_description = models.TextField(
        blank=True,
        help_text="Open Graph description (social share description)"
    )
    og_image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Open Graph image"
    )

    og_panels = [
        MultiFieldPanel(
            [
                FieldPanel("og_title"),
                FieldPanel("og_description"),
                FieldPanel("og_image"),
            ],
            heading="Open Graph Data",
        )
    ]

    class Meta:
        abstract = True
