"""Dashboard ModelForms.

A small ``StyledModelForm`` base applies consistent Tailwind classes to every
widget so the custom dashboard forms look cohesive without per-field markup.
"""

from django import forms
from django.forms import inlineformset_factory

from blog.models import BlogPost
from core.models import Experience, Skill, SiteSettings, Testimonial
from projects.models import Category, Project, ProjectImage, Technology

BASE_INPUT = (
    "w-full rounded-lg border border-slate-300 dark:border-white/10 "
    "bg-white dark:bg-white/5 px-3 py-2 text-sm text-slate-800 dark:text-slate-100 "
    "focus:border-accent focus:ring-2 focus:ring-accent/30 outline-none transition"
)
CHECKBOX = "h-4 w-4 rounded border-slate-300 text-accent focus:ring-accent"


class MultipleFileInput(forms.ClearableFileInput):
    """A file input that allows selecting several files at once."""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """File field that cleans a list of uploaded files (for multi-select)."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"multiple": True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single = super().clean
        if isinstance(data, (list, tuple)):
            return [single(d, initial) for d in data if d]
        return [single(data, initial)] if data else []


class StyledModelForm(forms.ModelForm):
    """Applies Tailwind classes to all widgets automatically and exposes a few
    helpers the generic template uses for a friendlier layout."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            # Leave the rich-text editor and hidden inputs untouched.
            if widget.__class__.__name__.startswith("CKEditor"):
                continue
            if isinstance(widget, forms.CheckboxSelectMultiple):
                # No class here — it would land on the OUTER container and the
                # individual inputs. The .checkbox-grid CSS styles them instead.
                pass
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", CHECKBOX)
            elif isinstance(widget, (forms.FileInput, forms.ClearableFileInput)):
                widget.attrs.setdefault(
                    "class",
                    "block w-full text-sm text-slate-500 file:mr-3 file:py-2 "
                    "file:px-4 file:rounded-lg file:border-0 file:bg-accent "
                    "file:text-white file:text-sm hover:file:bg-accent/90 cursor-pointer",
                )
            elif isinstance(widget, forms.SelectMultiple):
                widget.attrs.setdefault("class", BASE_INPUT + " min-h-[8rem]")
            else:
                widget.attrs.setdefault("class", BASE_INPUT)

    # --- Layout helpers consumed by templates/dashboard/generic_form.html ---
    @property
    def image_field_names(self):
        """Names of file/image fields (so the template can show a preview)."""
        return [
            n for n, f in self.fields.items()
            if isinstance(f.widget, (forms.ClearableFileInput, forms.FileInput))
        ]

    @property
    def checkbox_group_field_names(self):
        """Names of multi-checkbox fields (rendered as a tag grid)."""
        return [
            n for n, f in self.fields.items()
            if isinstance(f.widget, forms.CheckboxSelectMultiple)
        ]

    @property
    def wide_field_names(self):
        """Fields that should span the full form width (vs. half in a 2-col grid)."""
        wide = []
        for n, f in self.fields.items():
            w = f.widget
            if (
                isinstance(w, (forms.Textarea, forms.SelectMultiple,
                               forms.CheckboxSelectMultiple,
                               forms.ClearableFileInput, forms.FileInput))
                or w.__class__.__name__.startswith("CKEditor")
            ):
                wide.append(n)
        return wide


class ProjectForm(StyledModelForm):
    # Multi-select "sub images" — saved as gallery images by the view.
    sub_images = MultipleFileField(
        required=False,
        label="Sub images (gallery)",
        help_text="Select one or more images (hold Ctrl/Cmd to pick several). "
                  "These become the project's gallery images shown lower on the "
                  "project page. Existing ones are listed below to edit or remove.",
    )

    field_order = [
        "title", "slug", "short_description", "description",
        "main_image", "sub_images",
        "technologies", "category", "live_url", "github_url",
        "status", "is_featured", "order",
    ]

    class Meta:
        model = Project
        fields = [
            "title", "slug", "short_description", "description",
            "main_image",
            "technologies", "category", "live_url", "github_url",
            "status", "is_featured", "order",
        ]
        widgets = {
            "short_description": forms.TextInput(),
            "description": forms.Textarea(attrs={"rows": 8}),
            "slug": forms.TextInput(attrs={"placeholder": "auto-generated if blank"}),
            "technologies": forms.CheckboxSelectMultiple(),
        }
        labels = {
            "main_image": "Main image",
        }
        help_texts = {
            "main_image": "The primary image — shown on the project card and as the "
                          "big image at the top of the project page.",
            "category": 'Choose a category. Need a new one? '
                        '<a href="/dashboard/categories/add/" target="_blank" '
                        'class="text-accent underline">+ Add category</a>',
            "technologies": 'Tick the technologies used. Need a new one? '
                            '<a href="/dashboard/technologies/add/" target="_blank" '
                            'class="text-accent underline">+ Add technology</a>',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False


# Inline formset to MANAGE existing gallery images (edit caption/order, delete).
# New images are added via the ProjectForm "sub_images" multi-upload, so no
# empty "add" rows are needed here.
ProjectImageFormSet = inlineformset_factory(
    Project, ProjectImage,
    fields=["image", "caption", "order"],
    extra=0, can_delete=True,
    widgets={
        "caption": forms.TextInput(attrs={"class": BASE_INPUT}),
        "order": forms.NumberInput(attrs={"class": BASE_INPUT}),
    },
)


class ExperienceForm(StyledModelForm):
    class Meta:
        model = Experience
        fields = [
            "title", "organization", "type", "location",
            "start_date", "end_date", "description", "order",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "end_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure existing dates pre-fill the HTML date inputs.
        for f in ("start_date", "end_date"):
            self.fields[f].input_formats = ["%Y-%m-%d"]


class SkillForm(StyledModelForm):
    class Meta:
        model = Skill
        fields = ["name", "icon", "category", "proficiency_percent", "order"]


class BlogPostForm(StyledModelForm):
    class Meta:
        model = BlogPost
        fields = [
            "title", "slug", "excerpt", "content",
            "featured_image", "status", "published_at",
        ]
        widgets = {
            "excerpt": forms.Textarea(attrs={"rows": 2}),
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"},
                                                format="%Y-%m-%dT%H:%M"),
            "slug": forms.TextInput(attrs={"placeholder": "auto-generated if blank"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["published_at"].required = False
        self.fields["published_at"].input_formats = ["%Y-%m-%dT%H:%M"]


class TestimonialForm(StyledModelForm):
    class Meta:
        model = Testimonial
        fields = ["name", "role", "company", "photo", "message", "rating",
                  "order", "is_active"]
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}


class CategoryForm(StyledModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug", "order"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False


class TechnologyForm(StyledModelForm):
    class Meta:
        model = Technology
        fields = ["name", "slug", "icon"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False


class SiteSettingsForm(StyledModelForm):
    class Meta:
        model = SiteSettings
        exclude = ["updated_at"]
        widgets = {
            "about_text": forms.Textarea(attrs={"rows": 5}),
            "meta_description": forms.Textarea(attrs={"rows": 2}),
        }
