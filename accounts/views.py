from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


class DashboardLoginView(auth_views.LoginView):
    """Owner login for the dashboard. No public registration is exposed."""

    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class DashboardLogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("core:home")
