import os
from pathlib import Path

# ======================================================
# BASE DIR
# ======================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ======================================================
# SECURITY
# ======================================================

SECRET_KEY = 'django-insecure-vj0@he!#u32)(2pk_@xyc_nqwqm962x(#-93qj9*n&s#8%emz)'

DEBUG = True

ALLOWED_HOSTS = []


# ======================================================
# APPLICATIONS
# ======================================================

INSTALLED_APPS = [

    # DJANGO
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # CRISPY
    'crispy_forms',
    'crispy_bootstrap5',

    # APPS
    'servicios',
    'reservas',
    'usuarios',
    'productos',
    'configuraciones',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# ======================================================
# MIDDLEWARE
# ======================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ======================================================
# URLS
# ======================================================

ROOT_URLCONF = 'core.urls'


# ======================================================
# TEMPLATES
# ======================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],

        'APP_DIRS': True,

        'OPTIONS': {

            'context_processors': [

                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',

                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ======================================================
# WSGI
# ======================================================

WSGI_APPLICATION = 'core.wsgi.application'


# ======================================================
# DATABASE
# ======================================================

DATABASES = {
    'default': {

        'ENGINE': 'django.db.backends.sqlite3',

        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ======================================================
# PASSWORD VALIDATION
# ======================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },

    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },

    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },

    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ======================================================
# LANGUAGE
# ======================================================

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True


# ======================================================
# STATIC FILES
# ======================================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]


# ======================================================
# MEDIA FILES
# ======================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# ======================================================
# LOGIN
# ======================================================

# CUANDO EL USUARIO NO ESTÁ LOGUEADO
# LO ENVÍA AL REGISTRO

LOGIN_URL = '/usuarios/registro/'

# DESPUÉS DEL LOGIN
LOGIN_REDIRECT_URL = '/'

# DESPUÉS DEL LOGOUT
LOGOUT_REDIRECT_URL = '/'


# ======================================================
# CUSTOM USER
# ======================================================

AUTH_USER_MODEL = 'usuarios.Usuario'


# ======================================================
# EMAIL
# ======================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp-relay.brevo.com'

EMAIL_PORT = 587

EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'aa9420001@smtp-brevo.com'

EMAIL_HOST_PASSWORD = 'CcHkS6yZ21UIJWw7'

DEFAULT_FROM_EMAIL = 'chichabarber39@gmail.com'


# ======================================================
# DEFAULT AUTO FIELD
# ======================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
