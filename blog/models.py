"""Blog models."""

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from django_ckeditor_5.fields import CKEditor5Field

from core.models import TimeStampedModel


class BlogPost(TimeStampedModel):
    """An article/blog post with rich-text content."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt = models.CharField(
        max_length=300, blank=True,
        help_text="Short summary shown in the blog list / read-more cards.",
    )
    content = CKEditor5Field(config_name="default")
    featured_image = models.ImageField(
        upload_to="blog/", blank=True, null=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="blog_posts",
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT,
    )
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Stamp publish time the first time a post goes live.
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED
