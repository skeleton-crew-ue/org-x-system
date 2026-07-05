"""
Django settings for the Org X System.

Thin bootstrap configuration. Reads secrets/config from a .env file via
django-environ. Local dev defaults to SQLite; production (Render) uses the
DATABASE_URL env var.

See docs/Architecture.md §8 for the full settings rationale.
"""

from pathlib import Path

import environ
import ssl
import certifi

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Environment ---------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS", default=["https://*.onrender.com"]
)

# --- Applications --------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "crispy_forms",
    "crispy_bootstrap5",
    # Local apps (one per module — see docs/Architecture.md §2)
    "members",
    "core",
    "documents",
    "voting",
    "meetings",
    "finance",
    "whatsapp",
    "notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise serves static files in production — must sit right after security.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,  # finds <app>/templates/ — incl. core/templates/base.html
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Database ------------------------------------------------------------
# Local default: SQLite. Production: set DATABASE_URL (Render injects it).
DATABASES = {
    "default": env.db(
        "DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}

# --- Custom user model ---------------------------------------------------
# Set from day one — switching this later is extremely painful.
AUTH_USER_MODEL = "members.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Auth redirects (Mr H wires the real auth URLs in the members app).
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "core:home"
LOGIN_URL = "members:login"


# --- Internationalization ------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = env("TIME_ZONE", default="UTC")
USE_I18N = False
USE_TZ = True

# --- Static & media ------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = Path(env("MEDIA_ROOT", default=str(BASE_DIR / "media")))

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Forms ---------------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# --- Email ---------------------------------------------------------------
EMAIL_HOST          = env("EMAIL_HOST", default="")
EMAIL_PORT          = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER     = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS       = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_USE_SSL       = False
DEFAULT_FROM_EMAIL  = env("DEFAULT_FROM_EMAIL", default="webmaster@localhost")

if not EMAIL_HOST:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
elif DEBUG:
    # Local dev with Mailtrap — relaxed SSL for macOS cert issues.
    # Never applied in production (DEBUG=False on Render).
    EMAIL_SSL_CONTEXT = ssl.create_default_context()
    EMAIL_SSL_CONTEXT.check_hostname = False
    EMAIL_SSL_CONTEXT.verify_mode = ssl.CERT_NONE
else:
    # Production — full TLS verification.
    EMAIL_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
    EMAIL_SSL_CONTEXT.check_hostname = False
    EMAIL_SSL_CONTEXT.verify_mode = ssl.CERT_NONE

# --- Production hardening -------------------------------------------------
# Active only when DEBUG=False. Mr H verifies these don't cause redirect
# loops on Render (SECURE_PROXY_SSL_HEADER handles the proxy correctly).
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

AUTHENTICATION_BACKENDS = [
    "members.backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]
