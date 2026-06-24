from django.urls import path

from . import views

app_name = "website"

urlpatterns = [
    # Homepage & contact
    path("", views.home, name="home"),
    path("contact/", views.contact, name="contact"),

    # Auth (dashboard login/logout)
    path("login/", views.DashboardLoginView.as_view(), name="login"),
    path("logout/", views.DashboardLogoutView.as_view(), name="logout"),

    # Projects
    path("projects/", views.ProjectListView.as_view(), name="project_list"),
    path("projects/<slug:slug>/", views.ProjectDetailView.as_view(), name="project_detail"),

    # Blog
    path("blog/", views.BlogListView.as_view(), name="blog_list"),
    path("blog/<slug:slug>/", views.BlogDetailView.as_view(), name="blog_detail"),
]
