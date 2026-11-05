# Progress

Steps match `ROADMAP.md`.

- [x] 0. Python toolchain
- [x] 1. Docker dev environment
- [x] 2. `startproject`
- [x] 3. First app, URLs, function views
- [x] 4. Templates
- [x] 5. Models, ORM, migrations
- [x] 6. The Django admin
- [ ] 7. Media uploads and images
- [ ] 8. Class-based views and the public site
- [ ] 9. Static files
- [ ] 10. Forms
- [ ] 11. Tests
- [ ] 12. Production settings
- [ ] 13. Deploy to mini-server

## Notes

### Step 0 (done 2026-10-27)

- Host venv: `.venv/` created with `python3.13` (3.13.17). Holds Django 5.2.18, Pillow 13, ruff.
- `requirements.txt`: `Django~=5.2.0`, `Pillow~=13.0`.
- Scratch exercises live in `~/Desktop/py-scratch/` (`crafts/materials.py`, `crafts/inventory.py`),
  outside the project.
- Covered: venv, pip/requirements, REPL, truthiness (`'0'` is truthy), list/dict/tuple/set and
  reference semantics, functions (keyword-only args, mutable default trap), modules/imports
  (`sys.modules` cache, `__name__`, shadowing stdlib), classes (explicit `self`, `__str__`/
  `__repr__`, `@property`, class vs instance attrs), exceptions (hierarchy, `except` tuples,
  `else`, EAFP vs LBYL, no bare `except`), `Decimal` over `float` for quantities, PEP 8 + ruff.
- Editor: Sublime Text 4 (build 4215) with EditorConfig, LSP and LSP-ruff. Format and fix on
  save for Python via `Python.sublime-settings`.

### Step 1 (done 2026-10-28)

- `Dockerfile`: `python:3.13-slim`, `PYTHONUNBUFFERED=1`, `PYTHONDONTWRITEBYTECODE=1`,
  `WORKDIR /app`, requirements copied and installed first for layer caching. No venv in the
  image, and no source `COPY` (dev-only image; prod on mini-server uses a venv + Gunicorn).
- `compose.yaml`: one service named **`server`**, `build: .`, bind mount `.:/app`, ports
  **`"8001:8000"`** (host 8000 is taken by the `knowledge-direct-8-api` container).
- `requirements-dev.txt`: `-r requirements.txt` + `ruff~=0.17.0`. Host venv was rebuilt from it.
- Covered: why the container replaces the venv, compose.yaml structure and YAML basics, bind
  mounts vs image `site-packages`, host:container ports, `-r` includes, `~=` on 0.x versions,
  pip never uninstalls (recreate the venv instead).
- Fixed a bug in global `~/.editorconfig`: `[*.yaml, *.yml]` matched nothing (so YAML got tabs);
  the correct header is `[*.{yaml,yml}]`.

### Step 2 (done 2026-10-28)

- Project package is named **`config`** (`django-admin startproject config .`, run inside the
  container). It's a neutral name, so the working name "craft" never appears in import paths.
- Compose command is now `python manage.py runserver 0.0.0.0:8000`. Site at
  http://localhost:8001.
- Covered: `docker compose run --rm` (one-off) vs `exec` (running container); `manage.py` and
  `os.environ.setdefault` for `DJANGO_SETTINGS_MODULE`; `settings.py` is Python (`BASE_DIR`,
  `Path /`, only UPPER_CASE names count); `manage.py`/`wsgi.py`/`asgi.py` are alternative entry
  points that all load settings and then `ROOT_URLCONF`; WSGI ≈ the FastCGI contract;
  `runserver` autoreload; modules load once per process (demonstrated with a `print` in
  `urls.py`) and module state is per process, never shared between Gunicorn workers; reading a
  Django traceback (last line, then `/app/` frames; a broken settings string fails inside
  `import_module`).
- 18 unapplied migrations are pending, deliberately, until Step 5.

### Step 3 (done 2026-10-28)

- App `portfolio` created and added to `INSTALLED_APPS` (short form `"portfolio"`).
- `config/urls.py` mounts `include("portfolio.urls")` at the empty prefix `""`.
  `portfolio/urls.py` has `app_name = "portfolio"`, with routes `""` → `home` (name `home`) and
  `"about/"` → `about` (name `about`).
- Covered: project vs app (≈ Phalcon modules), the silent `INSTALLED_APPS` bug, function views
  (request in, `HttpResponse` out, no superglobals), `path()`/`include()` prefix joining, no
  leading slash, trailing slashes and `APPEND_SLASH`, the debug 404 page, explicit routing (no
  convention-based wildcard routes, on purpose), the module-level counter (persists, resets on
  reload, per process, not thread-safe; needs `global` to assign), `request.GET.get()`, reflected
  XSS and escaping on output (`django.utils.html.escape` ≈ `htmlspecialchars`).
- **Deferred:** `reverse()` and `{% url %}`. Eric found them confusing before there were enough
  links to justify them. Reintroduce once hard-coded paths start to hurt (likely Step 8).
- The visit counter was removed. Rebuild it with the database as a first exercise in Step 5
  (the wrong way vs the right way).

### Step 4 (done 2026-10-28)

- `TEMPLATES["DIRS"] = [BASE_DIR / "templates"]`. Site layout in `templates/base.html`, with
  blocks `meta_title_text` (in `<title>`, rendered as "Page | Craft"), `page_title_text` (the
  `<h1>`) and `content`. Nav uses hard-coded `/` and `/about/` links.
- App templates are namespaced: `portfolio/templates/portfolio/{home,about}.html`.
- Views use `render()`. `home` greets `?name=` with `{{ name|title }}`. `about` lists
  `crafts` with `{% for %}`/`{% empty %}`.
- Covered: `loader.get_template` (long way) then `render()`, context dicts, auto-escaping and
  `|safe` (XSS demo), `{% extends %}`/`{% block %}` (content outside blocks is dropped),
  `{{ block.super }}`, filters (`title` ≈ `ucwords`, `capfirst` ≈ `ucfirst`, `default` uses
  truthiness), the template search order (`DIRS` first, then apps; project overrides apps,
  compared to Drupal's core/module/theme layers; Django has no automatic "suggestions"),
  `{% if %}`/`{% for %}`/`{% empty %}`.

### Step 5 (done 2026-11-02)

- All 18 built-in migrations applied. `portfolio` migrations `0001`–`0005` applied:
  - `Visit` (`path`, `visited_at` auto_now_add): one row per page view, recorded in both views.
    The home page shows the count for `request.path`. This replaces the module-level counter.
  - `Project`: `title`, `slug` (unique, `max_length=200`), `description`/`materials` (text,
    `blank`), `made_on` (date, `null`+`blank`), `featured` (default False),
    `tags` (M2M → `Tag`, `blank`, `related_name="projects"`). Ordering `("-made_on", "-id")`.
  - `Photo`: `project` FK (`CASCADE`, `related_name="photos"`), `image`
    (`ImageField(upload_to="photos/")`), `caption` (text, `blank`), `alt_text` (required text),
    `order` (`PositiveSmallIntegerField(default=0)`). Ordering `("order", "id")`.
  - `Tag`: unique `name` and `slug` (`max_length=100`). Ordering `("name",)`.
- Sample data entered in the shell: 4 projects (Sarah Bernhardt (featured, 2025-10-12), Daisy
  Chair (2025-07-31), Curtains, Blue Velvet Chair) and tags Furniture, Art, Mid-Century. No
  photos yet.
- Covered: migrations and `django_migrations`, `showmigrations`/`makemigrations`/`sqlmigrate`/
  `migrate`, reading generated migrations, `AlterField` and SQLite's table rebuild, migration
  `dependencies` chain, deleting and regenerating an unapplied migration, field types and
  options (`blank` vs `null`, `unique`, `default` is Python-side, not a DB DEFAULT),
  `default_auto_field` in `apps.py`, `Meta.ordering` with a tie-breaker (NULLs sort last on
  SQLite DESC), tuples in `Meta` to satisfy ruff RUF012, `ForeignKey` (`on_delete`,
  `related_name`, column on the child only), `ManyToManyField` (implicit join table
  `<app>_<model>_<field>`), `save()` vs `objects.create()`, M2M needs saved objects,
  `datetime.date`/`timedelta`/`strftime` vs PHP `DateTime`, `timezone.now()` with `USE_TZ`,
  QuerySets (`filter`, `exclude`, `get` and `Model.DoesNotExist`, `__isnull`, `__in`,
  `relation__field` joins, `.distinct()` for join duplicates, `.query`), laziness, N+1 and
  `prefetch_related` (measured 5 → 2 queries), `select_related` (explained, not yet used),
  REPL block rules in `manage.py shell` (no auto-indent; blank line ends a block),
  list comprehensions (≈ `array_map`).
- **Deferred to Step 7:** automatic per-project photo numbering (override `save()` with a
  `Max` aggregate).

### Step 6 (done 2026-11-05)

- Superuser created with `createsuperuser`. Admin at http://localhost:8001/admin/.
- `portfolio/admin.py`:
  - `ProjectAdmin`: `list_display` (title, made_on, featured), `search_fields` (title,
    description, materials, `tags__name`), `list_filter` (featured, tags, made_on),
    `prepopulated_fields` slug ← title, `inlines = (PhotoInline,)`.
  - `PhotoInline(TabularInline)` with `extra = 1`.
  - `TagAdmin`: `list_display` (name, slug), slug prepopulated from name.
  - `Photo` stays registered on its own (plain `register`) so all photos can be seen in one list.
  - `Visit` deliberately not registered (it was a teaching model).
- Covered: auth users, `is_staff`/`is_superuser`, password hashing (`set_password` ≈
  `password_hash`, never assign `password` directly), admin autodiscovery of each app's
  `admin.py`, explicit registration (no automatic model admin), widgets derived from field
  types, form validation (unique check) vs DB constraint (`IntegrityError` from the shell),
  `ModelAdmin` subclasses as declarative config and passing a class (not an instance) to
  `register()`, M2M not allowed in `list_display` (`admin.E109`), NULL sort order (SQLite:
  smallest; PostgreSQL: largest; `nulls_last=`), the admin's pk tie-breaker, `search_fields`
  (`icontains`, OR across fields, AND across words, `relation__field` uses the *field* name,
  reverse uses `related_name`), `list_filter` (query-string params are ORM lookups, e.g.
  `made_on__isnull=True`), `prepopulated_fields` (client-side, add form only), the
  one-element tuple trap `("title",)`, `# noqa: RUF012` for false positives on class-level
  dicts, inlines and formsets.
- **Carried forward:**
  - Step 7: drag-and-drop photo reordering (`django-admin-sortable2` or hand-written JS over a
    hidden `order` field), and a `PhotoAdmin` with project column and thumbnail.
  - Step 10: if RUF012 keeps appearing (forms), replace `noqa` comments with a project
    `ruff.toml`.
  - Step 12: remove or replace `Visit` before deploying (a `DeleteModel` migration).
  - `@admin.register` decorator not introduced yet (Python decorators to come).

### Gotchas and decisions

- **Python 2.7 is on `PATH` outside a venv.** An old python.org framework install means plain
  `python` resolves to 2.7 when no venv is active. Always check for `(.venv)` in the prompt.
  Uninstalling it is optional, and Eric's call.
- Spelling: use American `color` in project code. Mixing `colour`/`color` caused bugs in
  exercises.
- Dev-only tools (ruff, etc.) go in `requirements-dev.txt`, not `requirements.txt`.
- Git: first commit `0257da0` ("initial commit, before Django admin"). Eric is adding a remote
  repo. **From now on, commit after each exercise and at the end of each step.**
  `.gitignore` covers `*.sublime-workspace` (`craft.sublime-project` is tracked). `SECRET_KEY`
  in `settings.py` is the dev key; it moves to env in Step 12, and must not be reused in prod
  since it's now in git history.
- `~/.editorconfig` still needs an `[*.html]` section (templates use tabs; it's easy to end up
  with mixed indentation).
- Teaching preferences: one exercise at a time; the long way before shortcuts; Claude reads
  files directly instead of asking Eric to paste them.

## Open questions

- Final site name and domain.
