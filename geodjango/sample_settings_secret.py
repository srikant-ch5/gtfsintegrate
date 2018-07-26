ALLOWED_HOSTS = ['*']

# WSGI_APPLICATION = 'gtfsintegrate.wsgi.application'

SECRET_KEY = ''

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',  # '127.0.0.1' probably works also
        'PORT': '5432',
    }
}
