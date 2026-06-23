from django.views.generic import DetailView, ListView

from .models import Category, Project


class ProjectListView(ListView):
    """All published projects with category filter buttons."""

    model = Project
    template_name = "projects/list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return (
            Project.objects.filter(status=Project.Status.PUBLISHED)
            .prefetch_related("technologies")
            .select_related("category")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.filter(
            projects__status=Project.Status.PUBLISHED
        ).distinct()
        return ctx


class ProjectDetailView(DetailView):
    """A single project with its gallery and related projects."""

    model = Project
    template_name = "projects/detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.filter(
            status=Project.Status.PUBLISHED
        ).prefetch_related("technologies", "gallery")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["related"] = (
            Project.objects.filter(
                status=Project.Status.PUBLISHED, category=self.object.category
            )
            .exclude(pk=self.object.pk)
            .prefetch_related("technologies")[:3]
        )
        return ctx
