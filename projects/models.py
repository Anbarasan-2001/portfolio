"""Portfolio project models: categories, technologies, projects and their
gallery images."""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.models import TimeStampedModel


class Category(models.Model):
    """A grouping used for the project filter (e.g. Web, Mobile, Design)."""

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Technology(models.Model):
    """A tech tag (e.g. Django, React) attached to projects."""

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    icon = models.CharField(
        max_length=120, blank=True,
        help_text="Optional icon CSS class for the tag.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Technologies"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Project(TimeStampedModel):
    """A portfolio project shown on the public site and managed in the dashboard."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    short_description = models.CharField(
        max_length=255,
        help_text="One-line summary shown on the project card.",
    )
    description = models.TextField(help_text="Full description for the detail page.")
    main_image = models.ImageField(
        upload_to="projects/main/", blank=True,
        help_text="Primary image — shown on the project card and at the top of "
                  "the project page.",
    )
    sub_image = models.ImageField(
        upload_to="projects/sub/", blank=True,
        help_text="Optional secondary image shown on the project page.",
    )
    # Legacy field kept for back-compat; new uploads use main_image.
    thumbnail = models.ImageField(upload_to="projects/thumbnails/", blank=True)

    technologies = models.ManyToManyField(
        Technology, related_name="projects", blank=True,
    )
    category = models.ForeignKey(
        Category, related_name="projects", on_delete=models.SET_NULL,
        null=True, blank=True,
    )

    live_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT,
    )
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower first).")

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"slug": self.slug})

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    @property
    def card_image(self):
        """Primary image to display, falling back to the legacy thumbnail."""
        return self.main_image or self.thumbnail


class ProjectImage(models.Model):
    """An additional gallery image belonging to a project."""

    project = models.ForeignKey(
        Project, related_name="gallery", on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to="projects/gallery/")
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Image for {self.project.title}"
