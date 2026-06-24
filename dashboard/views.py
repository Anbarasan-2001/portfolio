"""Custom dashboard: a styled, login-protected admin separate from Django's.

CRUD is built on generic class-based views with thin per-model subclasses to
keep everything DRY. List/form/delete templates are shared and configured via
class attributes.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

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

from .forms import (
    BlogPostForm,
    CategoryForm,
    ExperienceForm,
    ProjectForm,
    ProjectImageFormSet,
    SiteSettingsForm,
    SkillForm,
    TechnologyForm,
)


# --------------------------------------------------------------------------- #
#  Base mixins
# --------------------------------------------------------------------------- #
class DashboardMixin(LoginRequiredMixin):
    login_url = reverse_lazy("website:login")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Sidebar unread badge, available on every dashboard page.
        ctx["unread_count"] = ContactMessage.objects.filter(is_read=False).count()
        return ctx


class BaseListView(DashboardMixin, ListView):
    """Generic list page. Subclasses set model, columns, and url names."""

    template_name = "dashboard/generic_list.html"
    paginate_by = 15
    page_title = ""
    add_label = "Add new"
    columns = []          # list of (label, dotted-attr)
    add_url = None         # url name
    edit_url = None        # url name (takes pk)
    delete_url = None      # url name (takes pk)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            page_title=self.page_title,
            columns=self.columns,
            add_url=self.add_url,
            add_label=self.add_label,
            edit_url=self.edit_url,
            delete_url=self.delete_url,
        )
        return ctx


class BaseCreateView(DashboardMixin, SuccessMessageMixin, CreateView):
    template_name = "dashboard/generic_form.html"
    page_title = ""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = self.page_title or f"Add {self.model._meta.verbose_name}"
        return ctx


class BaseUpdateView(DashboardMixin, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/generic_form.html"
    page_title = ""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = self.page_title or f"Edit {self.model._meta.verbose_name}"
        return ctx


class BaseDeleteView(DashboardMixin, DeleteView):
    template_name = "dashboard/generic_confirm_delete.html"


# --------------------------------------------------------------------------- #
#  Dashboard home (stats)
# --------------------------------------------------------------------------- #
class DashboardHome(DashboardMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["stats"] = {
            "projects": Project.objects.count(),
            "published_projects": Project.objects.filter(
                status=Project.Status.PUBLISHED
            ).count(),
            "posts": BlogPost.objects.count(),
            "messages": ContactMessage.objects.count(),
            "unread": ContactMessage.objects.filter(is_read=False).count(),
            "skills": Skill.objects.count(),
            "experiences": Experience.objects.count(),
        }
        ctx["recent_messages"] = ContactMessage.objects.all()[:5]
        ctx["recent_projects"] = Project.objects.all()[:5]
        return ctx


# --------------------------------------------------------------------------- #
#  Projects (with gallery inline formset)
# --------------------------------------------------------------------------- #
class ProjectList(BaseListView):
    model = Project
    page_title = "Projects"
    add_label = "Add project"
    columns = [("Title", "title"), ("Category", "category"),
               ("Status", "get_status_display"), ("Featured", "is_featured"),
               ("Order", "order")]
    add_url = "dashboard:project_add"
    edit_url = "dashboard:project_edit"
    delete_url = "dashboard:project_delete"


class ProjectGalleryMixin:
    """Shared handling of the ProjectImage inline formset."""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx["formset"] = ProjectImageFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            ctx["formset"] = ProjectImageFormSet(instance=self.object)
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        formset = ctx["formset"]
        self.object = form.save()
        # Save any multi-selected "sub images" as gallery entries.
        sub_images = form.cleaned_data.get("sub_images") or []
        start = self.object.gallery.count()
        for i, f in enumerate(sub_images):
            ProjectImage.objects.create(project=self.object, image=f, order=start + i)
        if formset.is_valid():
            formset.instance = self.object
            formset.save()
            return redirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(form=form))


class ProjectCreate(ProjectGalleryMixin, BaseCreateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy("dashboard:project_list")
    success_message = "Project created."


class ProjectUpdate(ProjectGalleryMixin, BaseUpdateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy("dashboard:project_list")
    success_message = "Project updated."


class ProjectDelete(BaseDeleteView):
    model = Project
    success_url = reverse_lazy("dashboard:project_list")


# --------------------------------------------------------------------------- #
#  Experience
# --------------------------------------------------------------------------- #
class ExperienceList(BaseListView):
    model = Experience
    page_title = "Experience & Education"
    add_label = "Add entry"
    columns = [("Title", "title"), ("Organization", "organization"),
               ("Type", "get_type_display"), ("Start", "start_date"),
               ("Order", "order")]
    add_url = "dashboard:experience_add"
    edit_url = "dashboard:experience_edit"
    delete_url = "dashboard:experience_delete"


class ExperienceCreate(BaseCreateView):
    model = Experience
    form_class = ExperienceForm
    success_url = reverse_lazy("dashboard:experience_list")
    success_message = "Entry created."


class ExperienceUpdate(BaseUpdateView):
    model = Experience
    form_class = ExperienceForm
    success_url = reverse_lazy("dashboard:experience_list")
    success_message = "Entry updated."


class ExperienceDelete(BaseDeleteView):
    model = Experience
    success_url = reverse_lazy("dashboard:experience_list")


# --------------------------------------------------------------------------- #
#  Skills
# --------------------------------------------------------------------------- #
class SkillList(BaseListView):
    model = Skill
    page_title = "Skills"
    add_label = "Add skill"
    columns = [("Name", "name"), ("Category", "get_category_display"),
               ("Proficiency", "proficiency_percent"), ("Order", "order")]
    add_url = "dashboard:skill_add"
    edit_url = "dashboard:skill_edit"
    delete_url = "dashboard:skill_delete"


class SkillCreate(BaseCreateView):
    model = Skill
    form_class = SkillForm
    success_url = reverse_lazy("dashboard:skill_list")
    success_message = "Skill created."


class SkillUpdate(BaseUpdateView):
    model = Skill
    form_class = SkillForm
    success_url = reverse_lazy("dashboard:skill_list")
    success_message = "Skill updated."


class SkillDelete(BaseDeleteView):
    model = Skill
    success_url = reverse_lazy("dashboard:skill_list")


# --------------------------------------------------------------------------- #
#  Blog posts
# --------------------------------------------------------------------------- #
class BlogList(BaseListView):
    model = BlogPost
    page_title = "Blog posts"
    add_label = "Add post"
    columns = [("Title", "title"), ("Status", "get_status_display"),
               ("Published", "published_at")]
    add_url = "dashboard:blog_add"
    edit_url = "dashboard:blog_edit"
    delete_url = "dashboard:blog_delete"


class BlogAuthorMixin:
    """Default the author to the current user on first save."""

    def form_valid(self, form):
        if not form.instance.author_id:
            form.instance.author = self.request.user
        return super().form_valid(form)


class BlogCreate(BlogAuthorMixin, BaseCreateView):
    model = BlogPost
    form_class = BlogPostForm
    success_url = reverse_lazy("dashboard:blog_list")
    success_message = "Post created."


class BlogUpdate(BlogAuthorMixin, BaseUpdateView):
    model = BlogPost
    form_class = BlogPostForm
    success_url = reverse_lazy("dashboard:blog_list")
    success_message = "Post updated."


class BlogDelete(BaseDeleteView):
    model = BlogPost
    success_url = reverse_lazy("dashboard:blog_list")


# --------------------------------------------------------------------------- #
#  Categories & Technologies (project taxonomy)
# --------------------------------------------------------------------------- #
class CategoryList(BaseListView):
    model = Category
    page_title = "Categories"
    add_label = "Add category"
    columns = [("Name", "name"), ("Slug", "slug"), ("Order", "order")]
    add_url = "dashboard:category_add"
    edit_url = "dashboard:category_edit"
    delete_url = "dashboard:category_delete"


class CategoryCreate(BaseCreateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy("dashboard:category_list")
    success_message = "Category created."


class CategoryUpdate(BaseUpdateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy("dashboard:category_list")
    success_message = "Category updated."


class CategoryDelete(BaseDeleteView):
    model = Category
    success_url = reverse_lazy("dashboard:category_list")


class TechnologyList(BaseListView):
    model = Technology
    page_title = "Technologies"
    add_label = "Add technology"
    columns = [("Name", "name"), ("Slug", "slug")]
    add_url = "dashboard:technology_add"
    edit_url = "dashboard:technology_edit"
    delete_url = "dashboard:technology_delete"


class TechnologyCreate(BaseCreateView):
    model = Technology
    form_class = TechnologyForm
    success_url = reverse_lazy("dashboard:technology_list")
    success_message = "Technology created."


class TechnologyUpdate(BaseUpdateView):
    model = Technology
    form_class = TechnologyForm
    success_url = reverse_lazy("dashboard:technology_list")
    success_message = "Technology updated."


class TechnologyDelete(BaseDeleteView):
    model = Technology
    success_url = reverse_lazy("dashboard:technology_list")


# --------------------------------------------------------------------------- #
#  Site settings (singleton)
# --------------------------------------------------------------------------- #
class SiteSettingsUpdate(DashboardMixin, SuccessMessageMixin, UpdateView):
    model = SiteSettings
    form_class = SiteSettingsForm
    template_name = "dashboard/settings_form.html"
    success_url = reverse_lazy("dashboard:settings")
    success_message = "Settings saved."

    def get_object(self, queryset=None):
        return SiteSettings.load()


# --------------------------------------------------------------------------- #
#  Contact messages
# --------------------------------------------------------------------------- #
class MessageList(BaseListView):
    model = ContactMessage
    template_name = "dashboard/messages.html"
    page_title = "Contact messages"


@require_POST
def message_toggle_read(request, pk):
    if not request.user.is_authenticated:
        return redirect("website:login")
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = not msg.is_read
    msg.save(update_fields=["is_read"])
    messages.success(
        request, "Message marked as %s." % ("read" if msg.is_read else "unread")
    )
    return redirect("dashboard:messages")


class MessageDelete(BaseDeleteView):
    model = ContactMessage
    success_url = reverse_lazy("dashboard:messages")
