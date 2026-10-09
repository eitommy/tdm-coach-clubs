import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent


DEBUG = os.environ.get(
    "DEBUG",
    "True",
).lower() == "true"


SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "",
)

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-local-solo-desarrollo"
    else:
        raise ImproperlyConfigured(
            "Falta configurar SECRET_KEY en producción."
        )


ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

EXTRA_ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "",
)

for host in EXTRA_ALLOWED_HOSTS.split(","):
    host = host.strip()

    if host and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)


RENDER_EXTERNAL_HOSTNAME = os.environ.get(
    "RENDER_EXTERNAL_HOSTNAME"
)

if (
    RENDER_EXTERNAL_HOSTNAME
    and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS
):
    ALLOWED_HOSTS.append(
        RENDER_EXTERNAL_HOSTNAME
    )


CSRF_TRUSTED_ORIGINS = []

EXTRA_CSRF_TRUSTED_ORIGINS = os.environ.get(
    "CSRF_TRUSTED_ORIGINS",
    "",
)

for origin in EXTRA_CSRF_TRUSTED_ORIGINS.split(","):
    origin = origin.strip()

    if origin and origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

if RENDER_EXTERNAL_HOSTNAME:
    render_origin = (
        f"https://{RENDER_EXTERNAL_HOSTNAME}"
    )

    if render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(
            render_origin
        )


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "storages",
    "asistencia",
    "clubs",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "tdm_asistencia.urls"


TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends.django."
            "DjangoTemplates"
        ),
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                (
                    "django.template.context_processors."
                    "request"
                ),
                (
                    "django.contrib.auth.context_processors."
                    "auth"
                ),
                (
                    "django.contrib.messages.context_processors."
                    "messages"
                ),
                "clubs.context_processors.club_actual",
            ],
        },
    },
]


WSGI_APPLICATION = "tdm_asistencia.wsgi.application"


DATABASE_URL = os.environ.get(
    "DATABASE_URL"
)

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": (
                "django.db.backends.sqlite3"
            ),
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "NumericPasswordValidator"
        ),
    },
]


LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = []
STATIC_DIR = BASE_DIR / "static"

if STATIC_DIR.exists():
    STATICFILES_DIRS.append(
        STATIC_DIR
    )


# En local/tests no usamos manifest porque collectstatic todavía no corrió.
# En producción usamos WhiteNoise para servir archivos estáticos.
if DEBUG:
    STATICFILES_BACKEND = (
        "django.contrib.staticfiles.storage."
        "StaticFilesStorage"
    )
else:
    STATICFILES_BACKEND = (
        "whitenoise.storage."
        "CompressedStaticFilesStorage"
    )


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Media de producción (logos de clubes) en Cloudflare R2.
#
# Si NO están configuradas estas variables, seguimos usando el filesystem
# local exactamente como hasta ahora.
#
# Para activar R2 deben existir TODAS:
# - R2_ACCESS_KEY_ID
# - R2_SECRET_ACCESS_KEY
# - R2_BUCKET_NAME
# - R2_ENDPOINT_URL
# - R2_PUBLIC_DOMAIN
#
# R2_PUBLIC_DOMAIN debe ser solo el hostname, por ejemplo:
# media.tdmcoach.com
R2_ACCESS_KEY_ID = os.environ.get(
    "R2_ACCESS_KEY_ID",
    "",
).strip()

R2_SECRET_ACCESS_KEY = os.environ.get(
    "R2_SECRET_ACCESS_KEY",
    "",
).strip()

R2_BUCKET_NAME = os.environ.get(
    "R2_BUCKET_NAME",
    "",
).strip()

R2_ENDPOINT_URL = os.environ.get(
    "R2_ENDPOINT_URL",
    "",
).strip()

R2_PUBLIC_DOMAIN = os.environ.get(
    "R2_PUBLIC_DOMAIN",
    "",
).strip().removeprefix("https://").removeprefix("http://").rstrip("/")

R2_CONFIG = {
    "R2_ACCESS_KEY_ID": R2_ACCESS_KEY_ID,
    "R2_SECRET_ACCESS_KEY": R2_SECRET_ACCESS_KEY,
    "R2_BUCKET_NAME": R2_BUCKET_NAME,
    "R2_ENDPOINT_URL": R2_ENDPOINT_URL,
    "R2_PUBLIC_DOMAIN": R2_PUBLIC_DOMAIN,
}

R2_CONFIGURADO_PARCIALMENTE = any(
    R2_CONFIG.values()
)

R2_CONFIGURADO = all(
    R2_CONFIG.values()
)

if (
    R2_CONFIGURADO_PARCIALMENTE
    and not R2_CONFIGURADO
):
    faltantes = [
        nombre
        for nombre, valor in R2_CONFIG.items()
        if not valor
    ]

    raise ImproperlyConfigured(
        "Configuración R2 incompleta. Faltan: "
        + ", ".join(faltantes)
    )


if R2_CONFIGURADO:
    DEFAULT_STORAGE = {
    "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": R2_ACCESS_KEY_ID,
            "secret_key": R2_SECRET_ACCESS_KEY,
            "bucket_name": R2_BUCKET_NAME,
            "endpoint_url": R2_ENDPOINT_URL,
            "region_name": "auto",
            "custom_domain": R2_PUBLIC_DOMAIN,
            "querystring_auth": False,
            "file_overwrite": False,
            "default_acl": None,
        },
    }
else:
    DEFAULT_STORAGE = {
        "BACKEND": (
            "django.core.files.storage."
            "FileSystemStorage"
        ),
    }


STORAGES = {
    "default": DEFAULT_STORAGE,
    "staticfiles": {
        "BACKEND": STATICFILES_BACKEND,
    },
}


DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)


LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"


# Recuperación de contraseña.
# En local, si EMAIL_HOST está vacío, Django imprime el email completo
# en la terminal para poder probar el flujo sin SMTP real.
EMAIL_HOST = os.environ.get(
    "EMAIL_HOST",
    "",
)

if EMAIL_HOST:
    EMAIL_BACKEND = (
        "django.core.mail.backends.smtp.EmailBackend"
    )
    EMAIL_PORT = int(
        os.environ.get(
            "EMAIL_PORT",
            "587",
        )
    )
    EMAIL_HOST_USER = os.environ.get(
        "EMAIL_HOST_USER",
        "",
    )
    EMAIL_HOST_PASSWORD = os.environ.get(
        "EMAIL_HOST_PASSWORD",
        "",
    )
    EMAIL_USE_TLS = os.environ.get(
        "EMAIL_USE_TLS",
        "True",
    ).lower() == "true"
else:
    EMAIL_BACKEND = (
        "django.core.mail.backends.console."
        "EmailBackend"
    )

DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "TDM Coach <no-reply@tdmcoach.local>",
)


# URL base pública de la aplicación.
# En local apunta a 127.0.0.1; en Render se arma automáticamente.
APP_BASE_URL = os.environ.get(
    "APP_BASE_URL",
    "",
).rstrip("/")

if not APP_BASE_URL:
    if RENDER_EXTERNAL_HOSTNAME:
        APP_BASE_URL = (
            f"https://{RENDER_EXTERNAL_HOSTNAME}"
        )
    else:
        APP_BASE_URL = (
            "http://127.0.0.1:8000"
        )


if RENDER_EXTERNAL_HOSTNAME:
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )


# Endurecimiento básico cuando la app corre sin DEBUG.
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}