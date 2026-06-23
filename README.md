# Portfolio Site

A professional, animated portfolio website with a custom admin dashboard, built
with **Django + Django REST Framework**, **Tailwind CSS**, and
**GSAP / Locomotive Scroll / AOS** for motion.

- **Public site:** scroll-driven single-page experience (hero, about, skills,
  projects, experience timeline, testimonials, blog, contact) — all content is
  database-driven and editable from the dashboard.
- **Custom dashboard** (`/dashboard/`): a styled, login-protected admin
  (separate from Django admin) to manage every piece of content.
- **Deployment-ready:** env-var config, PostgreSQL support, Whitenoise static
  serving, Gunicorn, security hardening when `DEBUG=False`.

---

## Tech stack

| Area | Tools |
|------|-------|
| Backend | Django 5, Django REST Framework |
| Database | PostgreSQL (prod) · SQLite (local fallback) |
| Frontend | Django templates, Tailwind CSS (CDN), vanilla JS |
| Animation | GSAP + ScrollTrigger, Locomotive Scroll, AOS |
| Forms | Django forms (+ crispy-tailwind available) |
| Rich text | django-ckeditor-5 (blog content) |
| Media | Pillow, django-cleanup (auto-removes orphaned files) |
| Config | django-environ |
| Static (prod) | Whitenoise (compressed, hashed) |
| Server | Gunicorn |

---

## Project structure

```
portfolio/
├── manage.py
├── requirements.txt        # Python dependencies
├── Procfile                # process types for Railway/Render/Heroku
├── runtime.txt             # Python version
├── .env.example            # copy to .env and fill in
├── portfolio_site/         # project config (settings, urls, wsgi)
├── core/                   # homepage, contact, SiteSettings, Skill,
│                           #   Experience, Testimonial, ContactMessage
│   └── management/commands/seed_demo.py   # demo data generator
├── projects/               # Project, ProjectImage, Category, Technology
├── blog/                   # BlogPost (CKEditor 5)
├── dashboard/              # custom admin (CRUD, stats, settings)
├── accounts/               # dashboard login / logout
├── templates/              # base.html, dashboard_base.html, partials
├── static/
│   ├── css/main.css
│   └── js/                 # theme · scroll · animations · particles ·
│                           #   carousel · form  (one concern per file)
└── media/                  # user uploads (gitignored)
```

---

## Local setup

> Prerequisites: **Python 3.11+**, and (optionally) PostgreSQL. Without
> Postgres the app uses SQLite automatically.

```bash
# 1. Clone & enter
git clone <your-repo-url> portfolio && cd portfolio

# 2. Virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Environment
cp .env.example .env        # then edit values as needed

# 5. Database
python manage.py migrate

# 6. (Optional) demo content + an admin user
python manage.py seed_demo --superuser
#   -> creates admin / admin12345   (CHANGE THIS!)
# or create your own:
python manage.py createsuperuser

# 7. Run
python manage.py runserver
```

- Public site: <http://127.0.0.1:8000/>
- Dashboard: <http://127.0.0.1:8000/dashboard/> (login required)
- Django admin (quick data entry): <http://127.0.0.1:8000/django-admin/>

### Seed command

```bash
python manage.py seed_demo               # add demo content (idempotent)
python manage.py seed_demo --flush       # wipe demo content first
python manage.py seed_demo --superuser   # also create admin/admin12345
```

Placeholder images are generated with Pillow, so no external assets are needed.

---

## Configuration (`.env`)

All settings are environment-driven. Key variables (full list in
[.env.example](.env.example)):

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Django secret — **set a long random value in prod** |
| `DEBUG` | `True` locally, `False` in production |
| `ALLOWED_HOSTS` | comma-separated hostnames |
| `CSRF_TRUSTED_ORIGINS` | comma-separated `https://` origins (prod) |
| `DATABASE_URL` | `postgres://user:pass@host:5432/db` — unset = SQLite |
| `EMAIL_BACKEND` + `EMAIL_*` | SMTP for contact-form notifications |
| `CONTACT_NOTIFY_EMAIL` | where contact messages are emailed |

When `DEBUG=False`, security settings (SSL redirect, HSTS, secure cookies) are
enabled automatically.

> **Email in dev:** defaults to the console backend — submitted contact
> messages are printed to the terminal (and saved to the DB).

---

## Editing content

Almost everything is editable from **`/dashboard/`** — no code changes needed:

- **Projects** (with gallery images, tech tags, categories, draft/published,
  ordering, featured flag)
- **Experience / education** timeline entries
- **Skills** with proficiency
- **Blog posts** (rich-text editor, featured image, draft/published)
- **Testimonials**
- **Contact messages** (read/unread, reply, delete)
- **Site settings** — hero text, about, resume PDF, profile photo, contact
  details, social links, SEO defaults

---

## Deployment

The app is ready for any platform that runs Django + Gunicorn (Railway, Render,
Fly.io, a VPS, etc.). General steps:

1. **Provision PostgreSQL** and set `DATABASE_URL`.
2. **Set environment variables** (at minimum):
   ```
   SECRET_KEY=<long-random-string>
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   CSRF_TRUSTED_ORIGINS=https://yourdomain.com
   DATABASE_URL=postgres://...
   # email (for contact notifications)
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=...
   EMAIL_HOST_USER=...
   EMAIL_HOST_PASSWORD=...
   DEFAULT_FROM_EMAIL=Portfolio <no-reply@yourdomain.com>
   CONTACT_NOTIFY_EMAIL=you@yourdomain.com
   ```
3. **Build / release:**
   ```bash
   pip install -r requirements.txt
   python manage.py collectstatic --noinput
   python manage.py migrate --noinput
   ```
   The included [`Procfile`](Procfile) runs `migrate` on release and serves with
   Gunicorn:
   ```
   release: python manage.py migrate --noinput
   web: gunicorn portfolio_site.wsgi --log-file -
   ```
4. **Create your admin user:** `python manage.py createsuperuser`.
5. Static files are served by **Whitenoise** (no separate web server needed).
   For media (user uploads) at scale, configure S3 or your platform's
   persistent volume and point `MEDIA_ROOT`/storage there.

### Platform notes

- **Railway / Render:** point the service at the repo; both auto-detect the
  `Procfile`. Add a PostgreSQL plugin and the env vars above.
- **VPS (nginx + gunicorn):** run Gunicorn behind nginx; let Whitenoise serve
  `/static/`, and serve `/media/` from nginx pointing at `MEDIA_ROOT`.

---

## Notes & next steps

- **Tailwind** is loaded via CDN for fast iteration. For production you can
  switch to a compiled build (`django-tailwind` or a standalone CLI) to purge
  unused classes and drop the CDN — templates won't need changes.
- **Animations degrade gracefully:** smooth scroll and GSAP are disabled for
  `prefers-reduced-motion` and on touch devices; content stays visible if any
  CDN fails to load.
- **Change the seeded `admin/admin12345` password** before going live.
