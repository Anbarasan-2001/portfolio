"""Template context processors for site-wide data."""

# Section anchors used by the navbar and active-section highlighting.
# (label, element id) — order defines nav order.
NAV_LINKS = [
    ("Home", "home"),
    ("About", "about"),
    ("Skills", "skills"),
    ("Projects", "projects"),
    ("Experience", "experience"),
    ("Blog", "blog"),
    ("Contact", "contact"),
]


def site_settings(request):
    """Expose the singleton SiteSettings to every template as ``site``.

    Defensive: returns ``None`` if the model/table isn't ready yet (e.g.
    before the first migration), so templates never crash during setup.
    """
    site = None
    try:
        from core.models import SiteSettings

        site = SiteSettings.load()
    except Exception:
        site = None
    return {"site": site, "nav_links": NAV_LINKS}
