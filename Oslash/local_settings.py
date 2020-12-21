DEBUG = True
TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django_twitter',
        'USER': 'hitesh',
        'PASSWORD': 'khats',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}