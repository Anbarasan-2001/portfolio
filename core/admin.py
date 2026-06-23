from django.contrib import admin

from .models import (
    ContactMessage,
    Experience,
    Skill,
    SiteSettings,
    Testimonial,
)


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


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "rating", "is_active", "order")
    list_filter = ("is_active", "rating")
    list_editable = ("is_active", "order")
    search_fields = ("name", "company")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message", "created_at")
    date_hierarchy = "created_at"
