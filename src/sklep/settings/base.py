"""
Django settings for sklep project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import os
import sys


CURRENT_SETTINGS = "BASE"

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['']

# Application definition

INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'polymorphic',
    'subdomains',
    'django.contrib.sites',
    'easy_pdf',
    'djmoney',

    # my apps
    'sklep',
    'products',
    'search',
    'carts',
    'orders',
    'accounts',
    'billing',
    'addresses',
    'analytics',
    'marketing',
    'wix',
    'geolocation',
    'infobox',
    'money',
]


MIDDLEWARE = [
    'django_bot_crawler_blocker.django_bot_crawler_middleware.CrawlerBlockerMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'sklep.subdomains.SubdomainMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # custom:
    'money.middleware.validate_products_prices.ValidateProductsPrices',
    'money.middleware.validate_products_prices.ValidateShippingPrices',
    'money.middleware.currency.SetCurrency'
]

# Remove some midllewares when UT runs
if 'test' in sys.argv:
    MIDDLEWARE = list(MIDDLEWARE)
    MIDDLEWARE.remove('django_bot_crawler_blocker.django_bot_crawler_middleware.CrawlerBlockerMiddleware')
    MIDDLEWARE.remove('money.middleware.validate_products_prices.ValidateProductsPrices')
    MIDDLEWARE.remove('money.middleware.validate_products_prices.ValidateShippingPrices')


ROOT_URLCONF = 'sklep.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'libraries':{
                        'tags': 'sklep.templatetags.tags',
                        },
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
            ],

        },
    },
]

WSGI_APPLICATION = 'sklep.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

# Bot crawler blocker settings
# Remember to create table: python3 manage.py createcachetable
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

MAX_ALLOWED_HITS_PER_IP = 500 # max allowed hits per IP_TIMEOUT time from an IP. Default 2000.
IP_HITS_TIMEOUT = 60 # timeout in seconds for IP in cache. Default 60.


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

# LANGUAGE_CODE = 'pl'

TIME_ZONE = 'Europe/Warsaw'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGE_CODE = 'pl'

LANGUAGES = (
    ('pl', 'Polski'),
    ('en', 'English'),
)

DEFAULT_CURRENCY = 'PLN'
CURRENCIES = ('PLN', 'USD', 'EUR')
CURRENCY_CHOICES = [('PLN', 'PLN zł'), ('USD', 'USD $'), ('EUR', 'EUR €')]

import moneyed
from moneyed.localization import _FORMATTER, DEFAULT

_FORMATTER.add_sign_definition('pl_PL', moneyed.USD, prefix='US$')
_FORMATTER.add_sign_definition('pl_PL', moneyed.EUR, prefix='€')
_FORMATTER.add_sign_definition('DEFAULT', moneyed.EUR, prefix='€')

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static_my_proj"),
]

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static_cdn", "static_root")

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static_cdn", "media_root")


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587
EMAIL_USE_TLS = True

MANAGERS = (('e.pl', "l.com"),)
ADMINS = MANAGERS

MAILCHIMP_API_KEY = ""
MAILCHIMP_DATA_CENTER = "us17"
MAILCHIMP_EMAIL_LIST_ID = ""


CORS_REPLACE_HTTPS_REFERER      = False
HOST_SCHEME                     = "http://"
SECURE_PROXY_SSL_HEADER         = None
SECURE_SSL_REDIRECT             = False
SESSION_COOKIE_SECURE           = False
CSRF_COOKIE_SECURE              = False
SECURE_HSTS_SECONDS             = None
SECURE_HSTS_INCLUDE_SUBDOMAINS  = False
SECURE_FRAME_DENY               = False

LOGIN_URL = "/accounts/login/"


# A dictionary of urlconf module paths, keyed by their subdomain.
SUBDOMAIN_URLCONFS = {
    None: ROOT_URLCONF,
    'www': ROOT_URLCONF,
    'biczysko': 'wix.urls',
    'test': ROOT_URLCONF,
}


SETTINGS_EXPORT = [
    'LANGUAGES',
    'CURRENCIES',
    'LANGUAGE_CODE',
    'CURRENT_SETTINGS',
    'DEFAULT_CURRENCY'
]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} | {asctime} | {module}.{funcName} | {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
            },
        'disable_in_ut': {
            '()': 'sklep.log.UtNotRunning',
            }

    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/sklep.log',
            'formatter': 'simple'
        },
        'file_django': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/sklep_django.log',
            'formatter': 'simple'
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'email_backend': EMAIL_BACKEND,
            'filters': ['require_debug_false', 'disable_in_ut'],
            'include_html': True,
        }
    },
    'loggers': {
        'sklep': {
            'handlers': ['file', 'console', 'mail_admins'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'django': {
            'handlers': ['file_django', 'console', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}