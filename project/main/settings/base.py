from dotenv import load_dotenv
from pathlib import Path
import os
import sentry_sdk


load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = os.path.join(BASE_DIR, 'static')
SECRET_KEY = os.getenv("SECRET_KEY", '+eNfB7D7yuok5wk0RkExOkHs4PCgm2jCyiJAWiUZvGIznEDMmF')
DEBUG = True #os.getenv("DEBUG",True)

PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET")

PAYPAL_API_BASE = os.environ.get("PAYPAL_API_BASE")

ALLOWED_HOSTS = ["*"]

# Application definition
# Core
CORE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'mozilla_django_oidc',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRDY_PARTY_APPS = [
    'drf_yasg',
    'rest_framework',
    "rest_framework_api_key",
    'corsheaders',

]

DJAGNO_APPS = [
    'accounts',
    'neksio_api',
    'zatca_api',
    'invoices',
    'products',
    'transactions',

]

INSTALLED_APPS = CORE_APPS + THIRDY_PARTY_APPS + DJAGNO_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    "mozilla_django_oidc.middleware.SessionRefresh",
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'





CORS_ALLOWED_ORIGINS = [
    "http://0.0.0.0:8000",
    "http://localhost:3000",
    "https://app.einvotca.com",
    "https://www.app.einvotca.com",
    "https://einvotca.com",
    "https://accounts.einvotca.com",
    "https://www.angelcaretransit.com",
    "https://blog.einvotca.com",
]
# CSRF_TRUSTED_ORIGINS = [
#     "https://api.einvotca.com",
#
#
# ]

AUTHENTICATION_BACKENDS = [
    'accounts.sso_handler.MyOIDCABackend',
    'django.contrib.auth.backends.ModelBackend',

]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = port = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        "rest_framework_api_key.permissions.HasAPIKey",
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'mozilla_django_oidc.contrib.drf.OIDCAuthentication',

    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',

    )
}

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

KEYCLOAK_ADMIN = "bilaljmal"
KEYCLOAK_ADMIN_PASSWORD = "*Sybole371"

STATIC_URL = '/static/'
STATIC_ROOT = '/neksio/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



sentry_sdk.init(
    dsn="https://4d38f0dfc05fe1f68355f1c3ac0a76b9@o4509745852121088.ingest.us.sentry.io/4509745853235200",
    send_default_pii=True,
    traces_sample_rate=1.0,
)


SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'SECURITY_PROTOCOL': 'https',
}