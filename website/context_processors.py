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
        from dashboard.models import SiteSettings

        site = SiteSettings.load()
    except Exception:
        site = None

    # The Blog section/link only make sense once there are published posts,
    # so drop the Blog nav link when none exist.
    links = NAV_LINKS
    try:
        from dashboard.models import BlogPost

        if not BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).exists():
            links = [pair for pair in NAV_LINKS if pair[1] != "blog"]
    except Exception:
        links = [pair for pair in NAV_LINKS if pair[1] != "blog"]

    return {"site": site, "nav_links": links}
