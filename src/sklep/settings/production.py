from .base import *
import os

CURRENT_SETTINGS = "PROD"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
MAILCHIMP_API_KEY = os.environ["MAILCHIMP_API_KEY"]
MYSQL_PASS = os.environ["MYSQL_PASS"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'naklisze.pl',
    '54.37.136.82',
    'www.naklisze.pl',
    'biczysko.naklisze.pl'
]


DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'naklisze',
        'USER': 'root',
        'PASSWORD': MYSQL_PASS,
        'HOST': 'localhost',
        'OPTIONS': {'sql_mode': 'TRADITIONAL', 'use_pure': True, 'use_unicode': True, 'charset': 'utf8mb4',
                            'collation': 'utf8mb4_general_ci','get_warnings':False},
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static_my_proj"),
]

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static_cdn", "static_root")

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static_cdn", "media_root")


CORS_REPLACE_HTTPS_REFERER      = True
HOST_SCHEME                     = "https://"
SECURE_PROXY_SSL_HEADER         = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT             = True
SESSION_COOKIE_SECURE           = True
CSRF_COOKIE_SECURE              = True
SECURE_HSTS_INCLUDE_SUBDOMAINS  = True
SECURE_HSTS_SECONDS             = 1000000
SECURE_FRAME_DENY               = True

FILE_UPLOAD_MAX_MEMORY_SIZE = 200000000


# 'django.contrib.sites', remember to add domain in admin/sites
# MUST MATCH DB ID!!!
SITE_ID = 2