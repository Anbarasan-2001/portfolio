from django.views.generic import DetailView, ListView

from .models import BlogPost


class BlogListView(ListView):
    """Paginated list of published blog posts."""

    model = BlogPost
    template_name = "blog/list.html"
    context_object_name = "posts"
    paginate_by = 9

    def get_queryset(self):
        return BlogPost.objects.filter(
            status=BlogPost.Status.PUBLISHED
        ).select_related("author")


class BlogDetailView(DetailView):
    """A single published blog post."""

    model = BlogPost
    template_name = "blog/detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["recent"] = (
            BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED)
            .exclude(pk=self.object.pk)[:3]
        )
        return ctx
