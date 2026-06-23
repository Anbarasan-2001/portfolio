from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from blog.models import BlogPost
from projects.models import Category, Project
from .forms import ContactForm
from .models import Experience, Skill, Testimonial


def home(request):
    """Public homepage — assembles every section from the database."""
    projects = (
        Project.objects.filter(status=Project.Status.PUBLISHED)
        .prefetch_related("technologies")
        .select_related("category")
    )
    skills = Skill.objects.all()
    # Group skills by category for the skills section.
    skills_by_category = {}
    for skill in skills:
        skills_by_category.setdefault(skill.get_category_display(), []).append(skill)

    context = {
        "projects": projects,
        "featured_projects": projects.filter(is_featured=True),
        "categories": Category.objects.filter(projects__in=projects).distinct(),
        "skills": skills,
        "skills_by_category": skills_by_category,
        "experiences": Experience.objects.all(),
        "testimonials": Testimonial.objects.filter(is_active=True),
        "posts": BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED)[:3],
        "contact_form": ContactForm(),
    }
    return render(request, "core/home.html", context)


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
        return redirect("core:home")

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
    return redirect("core:home")


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
        # Never let email failures break the user's submission.
        pass
