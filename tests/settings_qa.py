from api_yamdb.settings import *  # noqa: E501

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),  # noqa: E501
    }
}
