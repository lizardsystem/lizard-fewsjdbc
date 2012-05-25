import os

from lizard_ui.settingshelper import setup_logging
from lizard_ui.settingshelper import STATICFILES_FINDERS

DEBUG = True
LOG_JDBC_QUERIES = True
TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db',
        }
}

SITE_ID = 1
INSTALLED_APPS = [
    'lizard_fewsjdbc',
    'lizard_map',
    'lizard_ui',
    'lizard_security',
    'staticfiles',
    'compressor',
    'south',
    'django_extensions',
    'django_nose',
    'djangorestframework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    ]
ROOT_URLCONF = 'lizard_fewsjdbc.urls'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Used for django-staticfiles
TEMPLATE_CONTEXT_PROCESSORS = (
    # Default items.
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    # Needs to be added for django-staticfiles to allow you to use
    # {{ STATIC_URL }}myapp/my.css in your templates.
    'staticfiles.context_processors.static_url',
    )

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'nl-NL'
# For at-runtime language switching.  Note: they're shown in reverse order in
# the interface!
LANGUAGES = (
    ('en', 'English'),
    ('nl', 'Nederlands'),
)
# If you set this to False, Django will make some optimizations so as not to
# load the internationalization machinery.
USE_I18N = True

# SETTINGS_DIR allows media paths and so to be relative to this settings file
# instead of hardcoded to c:\only\on\my\computer.
SETTINGS_DIR = os.path.dirname(os.path.realpath(__file__))

# BUILDOUT_DIR is for access to the "surrounding" buildout, for instance for
# BUILDOUT_DIR/var/static files to give django-staticfiles a proper place
# to place all collected static files.
BUILDOUT_DIR = os.path.abspath(os.path.join(SETTINGS_DIR, '..'))


# Absolute path to the directory that holds user-uploaded media.
MEDIA_ROOT = os.path.join(BUILDOUT_DIR, 'var', 'media')
# Absolute path to the directory where django-staticfiles'
# "bin/django build_static" places all collected static files from all
# applications' /media directory.
STATIC_ROOT = os.path.join(BUILDOUT_DIR, 'var', 'static')
STATICFILES_FINDERS = STATICFILES_FINDERS

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
MEDIA_URL = '/media/'
# URL for the per-application /media static files collected by
# django-staticfiles.  Use it in templates like
# "{{ MEDIA_URL }}mypackage/my.css".
STATIC_URL = '/static_media/'
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.  Uses STATIC_URL as django-staticfiles nicely collects
# admin's static media into STATIC_ROOT/admin.
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'


MAP_SETTINGS = {
    'base_layer_type': 'OSM',  # OSM or WMS
    'projection': 'EPSG:900913',  # EPSG:900913, EPSG:28992
    'display_projection': 'EPSG:4326',  # EPSG:900913/28992/4326
    'startlocation_x': '550000',
    'startlocation_y': '6850000',
    'startlocation_zoom': '7',
    'base_layer_osm': (
        'http://tile.openstreetmap.nl/tiles/${z}/${x}/${y}.png'),
    }

# Set the default period in days.
DEFAULT_START_DAYS = -20
DEFAULT_END_DAYS = 5

try:
    # Import local settings that aren't stored in svn.
    from lizard_fewsjdbc.local_testsettings import *
except ImportError:
    pass
