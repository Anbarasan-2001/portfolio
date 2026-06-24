from django.contrib import admin

from .models import (
    BlogPost,
    Category,
    ContactMessage,
    Experience,
    Project,
    ProjectImage,
    Skill,
    SiteSettings,
    Technology,
)


# --------------------------------------------------------------------------- #
#  Site settings & profile content
# --------------------------------------------------------------------------- #
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("__str__", "email", "updated_at")

    def has_add_permission(self, request):
        # Singleton: prevent creating more than one row from the admin.
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "proficiency_percent", "order")
    list_filter = ("category",)
    list_editable = ("proficiency_percent", "order")
    search_fields = ("name",)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "type", "start_date", "end_date", "order")
    list_filter = ("type",)
    list_editable = ("order",)
    search_fields = ("title", "organization")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message", "created_at")
    date_hierarchy = "created_at"


# --------------------------------------------------------------------------- #
#  Portfolio
# --------------------------------------------------------------------------- #
class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image", "caption", "order")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "is_featured", "order", "created_at")
    list_filter = ("status", "is_featured", "category", "technologies")
    list_editable = ("status", "is_featured", "order")
    search_fields = ("title", "short_description", "description")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("technologies",)
    inlines = [ProjectImageInline]


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ("project", "caption", "order")
    list_filter = ("project",)


# --------------------------------------------------------------------------- #
#  Blog
# --------------------------------------------------------------------------- #
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "author", "published_at", "created_at")
    list_filter = ("status", "created_at", "author")
    list_editable = ("status",)
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    autocomplete_fields = ("author",)
