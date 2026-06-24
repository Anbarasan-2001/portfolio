from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardHome.as_view(), name="home"),

    # Projects
    path("projects/", views.ProjectList.as_view(), name="project_list"),
    path("projects/add/", views.ProjectCreate.as_view(), name="project_add"),
    path("projects/<int:pk>/edit/", views.ProjectUpdate.as_view(), name="project_edit"),
    path("projects/<int:pk>/delete/", views.ProjectDelete.as_view(), name="project_delete"),

    # Categories
    path("categories/", views.CategoryList.as_view(), name="category_list"),
    path("categories/add/", views.CategoryCreate.as_view(), name="category_add"),
    path("categories/<int:pk>/edit/", views.CategoryUpdate.as_view(), name="category_edit"),
    path("categories/<int:pk>/delete/", views.CategoryDelete.as_view(), name="category_delete"),

    # Technologies
    path("technologies/", views.TechnologyList.as_view(), name="technology_list"),
    path("technologies/add/", views.TechnologyCreate.as_view(), name="technology_add"),
    path("technologies/<int:pk>/edit/", views.TechnologyUpdate.as_view(), name="technology_edit"),
    path("technologies/<int:pk>/delete/", views.TechnologyDelete.as_view(), name="technology_delete"),

    # Experience
    path("experience/", views.ExperienceList.as_view(), name="experience_list"),
    path("experience/add/", views.ExperienceCreate.as_view(), name="experience_add"),
    path("experience/<int:pk>/edit/", views.ExperienceUpdate.as_view(), name="experience_edit"),
    path("experience/<int:pk>/delete/", views.ExperienceDelete.as_view(), name="experience_delete"),

    # Skills
    path("skills/", views.SkillList.as_view(), name="skill_list"),
    path("skills/add/", views.SkillCreate.as_view(), name="skill_add"),
    path("skills/<int:pk>/edit/", views.SkillUpdate.as_view(), name="skill_edit"),
    path("skills/<int:pk>/delete/", views.SkillDelete.as_view(), name="skill_delete"),

    # Blog
    path("blog/", views.BlogList.as_view(), name="blog_list"),
    path("blog/add/", views.BlogCreate.as_view(), name="blog_add"),
    path("blog/<int:pk>/edit/", views.BlogUpdate.as_view(), name="blog_edit"),
    path("blog/<int:pk>/delete/", views.BlogDelete.as_view(), name="blog_delete"),

    # Messages
    path("messages/", views.MessageList.as_view(), name="messages"),
    path("messages/<int:pk>/toggle/", views.message_toggle_read, name="message_toggle"),
    path("messages/<int:pk>/delete/", views.MessageDelete.as_view(), name="message_delete"),

    # Site settings
    path("settings/", views.SiteSettingsUpdate.as_view(), name="settings"),
]
