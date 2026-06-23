"""Sitemap definitions for SEO."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import BlogPost
from projects.models import Project


class StaticViewSitemap(Sitemap):
    """Top-level static pages."""

    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return ["core:home", "projects:list", "blog:list"]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return Project.objects.filter(status=Project.Status.PUBLISHED)

    def lastmod(self, obj):
        return obj.updated_at


class BlogSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED)

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {
    "static": StaticViewSitemap,
    "projects": ProjectSitemap,
    "blog": BlogSitemap,
}
