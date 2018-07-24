SECRET_KEY = '5@ch@sqd_+(4eaj2h60qofszfhuuxk#h#f#ehyb&b+drp@v0&s'

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'gtfsintegratedb4',
        'USER': 'sriks',
        'PASSWORD': 'sriks@123',
        'HOST': 'localhost',  # '127.0.0.1' probably works also
        'PORT': '5432',
    }
}
