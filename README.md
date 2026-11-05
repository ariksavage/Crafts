# Craft

A portfolio site for my craft projects: furniture, art and fabric work, with photos, materials
and tags. "Craft" is a working name.

It's also a hands-on exercise in learning Python and Django, coming from a PHP background.
The curriculum is in [`ROADMAP.md`](ROADMAP.md), and notes on each completed step are in
[`PROGRESS.md`](PROGRESS.md).

## Stack

- Python 3.13
- Django 5.2 LTS
- SQLite
- Pillow, for images
- Docker Compose for local development
- Planned for production: Gunicorn behind Apache, managed by systemd

## Running locally

You need Docker with Compose.

```bash
docker compose up --build
```

The site is at http://localhost:8001. Host port 8001 maps to port 8000 in the container.
Source is bind-mounted, so `runserver` reloads when files change.

On a fresh checkout, create the database and an admin user from a second terminal:

```bash
docker compose exec server python manage.py migrate
docker compose exec server python manage.py createsuperuser
```

The admin is at http://localhost:8001/admin/.

## Linting and formatting

Dev tools run from a host virtualenv rather than the container:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check .
ruff format .
```

## Layout

| Path | What it is |
|---|---|
| `config/` | Project package: settings, root URLconf, WSGI/ASGI entry points |
| `portfolio/` | The app: models (`Project`, `Photo`, `Tag`), views, URLs, admin |
| `portfolio/templates/portfolio/` | App templates |
| `templates/` | Site-wide templates (`base.html`) |
| `requirements.txt` | Runtime dependencies |
| `requirements-dev.txt` | Runtime dependencies plus dev tools (ruff) |

## Status

Work in progress. Steps 0–6 of the roadmap are done: the models, the templates and the Django
admin. Next up are photo uploads, the public project pages, forms, tests and deployment.
