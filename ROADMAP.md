# Roadmap

Each step lists what you build, the concepts it teaches, and the PHP reference points to compare
against. Do them in order, since each one builds on the last.

---

## 0. Python toolchain

**Build:** nothing in the repo yet. Get comfortable on the host.

- `python3 -m venv .venv` and activation. A virtualenv is a per-project interpreter plus
  packages. *PHP:* closest to `vendor/`, but Python itself is per-venv too.
- `pip install`, `requirements.txt`, `pip freeze`. *PHP:* `composer require`, `composer.json`,
  `composer.lock`. Note there is no lock file by default.
- The REPL (`python3`, later `manage.py shell`). *PHP:* `php -a` or psysh, but used much more.
- Language crash-course on the differences: indentation as syntax, `None`/`True`/`False`,
  lists/dicts/tuples vs PHP arrays, f-strings vs interpolation, `import` vs autoload, explicit
  `self`, keyword arguments, truthiness, exceptions.
- Style: PEP 8, `snake_case`, and `ruff` as linter/formatter (≈ PHP-CS-Fixer).

## 1. Docker dev environment

**Build:** `Dockerfile` (FROM `python:3.13-slim`), `requirements.txt` (Django 5.2), and a
`compose.yaml` that bind-mounts the source folder and exposes port 8000.

- Why the venv inside Docker is optional (the container *is* the isolation).
- `runserver` with autoreload. *PHP:* `php -S`, but this is a long-running process, not
  per-request.
- **The big mental shift:** PHP is shared-nothing per request. A Django process stays alive and
  serves many requests, so module-level state persists.
- *Compare:* `~/knowledge-direct-local` Docker setup.

## 2. `startproject`

**Build:** run `django-admin startproject` inside the container. Read every generated file.

- `manage.py` ≈ Phalcon devtools / an artisan-style CLI.
- `settings.py` is Python code, not YAML. *Compare:* `config.yml` + `config.local.yml`.
- `urls.py`, `wsgi.py`/`asgi.py`. WSGI ≈ the contract PHP-FPM fulfils for PHP.
- Project vs app: a project holds many reusable apps. *Compare:* Phalcon modules.
- `manage.py runserver`, `manage.py check`.

## 3. First app, URLs, function views

**Build:** `startapp portfolio`, a home view, and a URL route.

- `HttpRequest`/`HttpResponse` objects. *PHP:* `$_GET`/`$_POST`/`echo`, or Phalcon's
  `$this->request`/`$this->response`.
- URLconf (`path()`, `include()`, named routes, `reverse()`). *PHP:* Phalcon router or
  `.htaccess` rewrites.
- `INSTALLED_APPS`, and why forgetting it is the #1 beginner bug.

## 4. Templates

**Build:** a `base.html` layout, a home page, and a static about page.

- Django template language: `{% extends %}`, `{% block %}`, `{{ var|filter }}`, `{% url %}`.
  *Compare:* Volt is nearly the same syntax, since both descend from Jinja/Twig.
- Auto-escaping is on by default. `|safe` is the escape hatch.
- Deliberately limited logic in templates. Do the work in the view.
- Template lookup order (app `templates/` dirs vs `DIRS`).

## 5. Models, ORM, migrations

**Build:** `Project` (title, slug, description, materials, date made, featured), `Photo` (FK to
Project, image, caption, order), and `Tag` (M2M).

- Model classes, field types, `__str__`, `Meta.ordering`. *Compare:* Phalcon models.
- `makemigrations` → read the generated file → `migrate`. Migrations are generated from model
  diffs. *Compare:* KD's hand-applied per-tenant migrations.
- QuerySets: `filter`/`exclude`/`get`, chaining, **lazy evaluation**, `select_related` /
  `prefetch_related` (the N+1 problem).
- Practice in `manage.py shell`.

## 6. The Django admin

**Build:** register the models, customise `ModelAdmin` (list_display, search, filters,
prepopulated slug), and add a `Photo` inline on `Project`.

- `createsuperuser`.
- This is the payoff: a full CRUD back office with almost no code. There's no real PHP framework
  equivalent.

## 7. Media uploads and images

**Build:** upload photos through the admin, serve them in dev, and generate thumbnails.

- `MEDIA_ROOT`/`MEDIA_URL`, `upload_to`, why dev serving ≠ prod serving.
- Pillow for resizing (on save, or via a library like `django-imagekit`). *Compare:* the
  Imagick on-demand resizing on ariksavage.com.

## 8. Class-based views and the public site

**Build:** a project list (paginated, filter by tag) and a project detail page by slug.

- `ListView`/`DetailView`, overriding `get_queryset`/`get_context_data`.
- Classes, inheritance, and mixins in Python. *Compare:* PHP traits.
- `get_absolute_url`, `get_object_or_404`.

## 9. Static files

**Build:** your CSS/JS/images in `static/`, wired into the templates.

- `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT`, `{% static %}`, `collectstatic`.
  *Compare:* the Grunt `dist/` build on ariksavage.com.

## 10. Forms

**Build:** a contact form that emails you.

- `forms.Form`, `cleaned_data`, validation, `{% csrf_token %}`, the POST/redirect/GET pattern.
- Email backends (console in dev, SMTP in prod). *Compare:* ariksavage.com's contact config and
  msmtp on mini-server.

## 11. Tests

**Build:** model, view, and form tests.

- `django.test.TestCase`, the test client, the throwaway test DB. Optionally pytest +
  pytest-django. *Compare:* PHPUnit.

## 12. Production settings

**Build:** split or env-driven settings.

- Read secrets from env vars or `.env` (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`,
  `CSRF_TRUSTED_ORIGINS`).
- `manage.py check --deploy`.
- Logging config. *Compare:* the PHP error.log habit, and "200 doesn't mean it worked".

## 13. Deploy to mini-server

**Build:** the live site.

- `create-site <fqdn>`, a Python venv on the server, `pip install -r requirements.txt`.
- Gunicorn + a systemd unit (socket, workers, restart policy).
- Apache vhost: `ProxyPass` to Gunicorn, `Alias /static` and `/media` served directly by Apache.
  *Compare:* the existing `emby.ariksavage.com` proxy vhost.
- certbot for HTTPS.
- The deploy sequence: pull → pip install → migrate → collectstatic → restart.
- Optional: automate it with a self-hosted GitHub Actions runner (the `github-runner` convention).
- Backups: SQLite file + `media/` folded into the nightly backup cron.
