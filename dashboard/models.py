"""All data models for the project live here, in the dashboard app.

Grouped by concern:
  * Site-wide settings + contact messages
  * Profile content blocks: skills, experience/timeline
  * Portfolio: categories, technologies, projects + gallery images
  * Blog posts

The public ``website`` app reads these models; the dashboard app owns and
manages them.
"""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from django_ckeditor_5.fields import CKEditor5Field


class TimeStampedModel(models.Model):
    """Abstract base adding self-managed created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# --------------------------------------------------------------------------- #
#  Site settings & contact
# --------------------------------------------------------------------------- #
class SiteSettings(models.Model):
    """Singleton holding all editable, site-wide content.

    Always loaded via :meth:`load`, which guarantees a single row (pk=1) so
    templates can rely on ``site`` always existing.
    """

    # Branding
    brand_name = models.CharField(
        max_length=60, blank=True,
        help_text="Short name shown as the logo in the navbar and footer "
                  "(e.g. your name). Falls back to the hero title if left blank.",
    )

    # Hero
    hero_title = models.CharField(
        max_length=120, default="Hi, I'm Your Name",
        help_text="Main animated headline in the hero section.",
    )
    hero_subtitle = models.CharField(
        max_length=200, blank=True,
        default="Full-Stack Developer & Designer",
    )
    hero_cta_text = models.CharField(
        max_length=40, blank=True, default="View My Work",
    )

    # About
    about_heading = models.CharField(max_length=120, blank=True, default="About Me")
    about_text = models.TextField(
        blank=True,
        help_text="Short bio shown in the About section.",
    )
    profile_photo = models.ImageField(
        upload_to="site/", blank=True, null=True,
    )
    resume_file = models.FileField(
        upload_to="site/resume/", blank=True, null=True,
        help_text="Downloadable resume/CV (PDF).",
    )

    # Contact details
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)

    # Social links
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    dribbble_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)

    # SEO defaults
    meta_description = models.CharField(
        max_length=300, blank=True,
        help_text="Default meta description / Open Graph description.",
    )
    og_image = models.ImageField(
        upload_to="site/og/", blank=True, null=True,
        help_text="Default social-share image (Open Graph).",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        # Enforce singleton: there is only ever one row, with pk=1.
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Return the singleton, creating it with defaults if missing."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def social_links(self):
        """List of (label, url, icon-key) for populated social links."""
        candidates = [
            ("GitHub", self.github_url, "github"),
            ("LinkedIn", self.linkedin_url, "linkedin"),
            ("Twitter", self.twitter_url, "twitter"),
            ("Instagram", self.instagram_url, "instagram"),
            ("Dribbble", self.dribbble_url, "dribbble"),
            ("Website", self.website_url, "globe"),
        ]
        return [(label, url, icon) for label, url, icon in candidates if url]


class ContactMessage(TimeStampedModel):
    """A message submitted through the public contact form."""

    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.subject or '(no subject)'}"


# --------------------------------------------------------------------------- #
#  Profile content blocks
# --------------------------------------------------------------------------- #
class Skill(models.Model):
    """A single skill with a proficiency level, grouped by category."""

    class Category(models.TextChoices):
        FRONTEND = "frontend", "Frontend"
        BACKEND = "backend", "Backend"
        DATABASE = "database", "Database"
        DEVOPS = "devops", "DevOps & Tools"
        DESIGN = "design", "Design"
        OTHER = "other", "Other"

    name = models.CharField(max_length=80)
    icon = models.CharField(
        max_length=120, blank=True,
        help_text="Icon CSS class (e.g. a Devicon/Font Awesome class).",
    )
    proficiency_percent = models.PositiveSmallIntegerField(
        default=80,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.OTHER,
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower first).")

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Experience(models.Model):
    """A work or education entry for the animated timeline."""

    class Type(models.TextChoices):
        WORK = "work", "Work"
        EDUCATION = "education", "Education"

    title = models.CharField(max_length=160, help_text="Role or qualification.")
    organization = models.CharField(max_length=160)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.WORK)
    location = models.CharField(max_length=120, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(
        blank=True, null=True, help_text="Leave blank if this is current.",
    )
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-start_date"]

    def __str__(self):
        return f"{self.title} @ {self.organization}"

    @property
    def is_current(self):
        return self.end_date is None


# --------------------------------------------------------------------------- #
#  Portfolio: categories, technologies, projects
# --------------------------------------------------------------------------- #
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
        return reverse("website:project_detail", kwargs={"slug": self.slug})

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


# --------------------------------------------------------------------------- #
#  Blog
# --------------------------------------------------------------------------- #
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
        return reverse("website:blog_detail", kwargs={"slug": self.slug})

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED
