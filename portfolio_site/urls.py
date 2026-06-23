"""Root URL configuration for portfolio_site."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from core.sitemaps import SITEMAPS

urlpatterns = [
    path("django-admin/", admin.site.urls),  # built-in admin (data entry)
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    # Apps
    path("", include("core.urls")),
    path("projects/", include("projects.urls")),
    path("blog/", include("blog.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("accounts/", include("accounts.urls")),
    # SEO
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": SITEMAPS},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt", content_type="text/plain"
        ),
        name="robots",
    ),
]

# Serve user-uploaded media during development.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
