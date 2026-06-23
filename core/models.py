"""Core models: site-wide settings, contact messages, and the profile-driven
content blocks (skills, experience/timeline, testimonials)."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base adding self-managed created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SiteSettings(models.Model):
    """Singleton holding all editable, site-wide content.

    Always loaded via :meth:`load`, which guarantees a single row (pk=1) so
    templates can rely on ``site`` always existing.
    """

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


class Testimonial(models.Model):
    """A client/colleague testimonial for the carousel."""

    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120, blank=True)
    company = models.CharField(max_length=120, blank=True)
    photo = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    message = models.TextField()
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "-id"]

    def __str__(self):
        return f"{self.name} ({self.company})" if self.company else self.name


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
