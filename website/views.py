"""Public website views: homepage, contact handling, project & blog pages,
and the dashboard login/logout screens."""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from dashboard.models import BlogPost, Category, Experience, Project, Skill

from .forms import ContactForm


# --------------------------------------------------------------------------- #
#  Homepage
# --------------------------------------------------------------------------- #
def home(request):
    """Public homepage — assembles every section from the database."""
    projects = (
        Project.objects.filter(status=Project.Status.PUBLISHED)
        .prefetch_related("technologies")
        .select_related("category")
    )
    skills = Skill.objects.all()
    # Group skills by category, emitting categories in a fixed display order.
    CATEGORY_ORDER = [
        Skill.Category.BACKEND,
        Skill.Category.FRONTEND,
        Skill.Category.DATABASE,
        Skill.Category.DEVOPS,
        Skill.Category.DESIGN,
        Skill.Category.OTHER,
    ]
    grouped = {}
    for skill in skills:
        grouped.setdefault(skill.category, []).append(skill)
    skills_by_category = {
        Skill.Category(cat).label: grouped[cat]
        for cat in CATEGORY_ORDER
        if cat in grouped
    }

    context = {
        "projects": projects,
        "featured_projects": projects.filter(is_featured=True),
        "categories": Category.objects.filter(projects__in=projects).distinct(),
        "skills": skills,
        "skills_by_category": skills_by_category,
        "experiences": Experience.objects.all(),
        "posts": BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED)[:3],
        "contact_form": ContactForm(),
    }
    return render(request, "core/home.html", context)


# --------------------------------------------------------------------------- #
#  Contact
# --------------------------------------------------------------------------- #
def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


@require_POST
def contact(request):
    """Handle contact-form submissions: save, email-notify, respond.

    Supports both AJAX (JSON) and classic POST (redirect + flash message).
    """
    form = ContactForm(request.POST)
    if form.is_valid():
        message = form.save()
        _notify_owner(message)
        if _is_ajax(request):
            return JsonResponse(
                {"success": True, "message": "Thanks! Your message has been sent."}
            )
        messages.success(request, "Thanks! Your message has been sent.")
        return redirect("website:home")

    # Invalid
    if _is_ajax(request):
        return JsonResponse(
            {
                "success": False,
                "message": "Please fix the errors and try again.",
                "errors": form.errors.get_json_data(),
            },
            status=400,
        )
    messages.error(request, "Please correct the errors in the form.")
    return redirect("website:home")


def _notify_owner(message):
    """Send the owner an email notification for a new contact message."""
    subject = f"New contact message: {message.subject or '(no subject)'}"
    body = (
        f"From: {message.name} <{message.email}>\n"
        f"Subject: {message.subject}\n\n"
        f"{message.message}\n"
    )
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_NOTIFY_EMAIL],
            fail_silently=True,
        )
    except Exception:
        # Never let a mail error break the user's submission.
        pass


# --------------------------------------------------------------------------- #
#  Projects
# --------------------------------------------------------------------------- #
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


# --------------------------------------------------------------------------- #
#  Blog
# --------------------------------------------------------------------------- #
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


# --------------------------------------------------------------------------- #
#  Auth (dashboard login/logout)
# --------------------------------------------------------------------------- #
class DashboardLoginView(auth_views.LoginView):
    """Owner login for the dashboard. No public registration is exposed."""

    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class DashboardLogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("website:home")
