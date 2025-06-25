# dictionary_project/settings.py

from pathlib import Path # <-- Make sure this import is here

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent # <-- Make sure this definition is here

ROOT_URLCONF = 'dictionary_project.urls'


# dictionary_project/settings.py

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True # <--- Make sure this is True for development!


# The rest of your settings would follow below this.
# ...

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3', # This line will now work correctly
    }
}

# ... (rest of your settings) ...


# dictionary_project/settings.py

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates', # <--- Make sure this is 'DjangoTemplates'
        'DIRS': [], # This is usually empty unless you have project-wide templates
        'APP_DIRS': True, # <--- This MUST be True for Django to look in app/templates/app_name/
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

# dictionary_project/settings.py


# dictionary_project/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dictionary_app', # Add your new app here
]


# Add a SECRET_KEY if Django didn't automatically generate one
# (It usually does, but ensure it's there and strong in production)
# For development, you can use a placeholder:
# SECRET_KEY = 'your-secret-key-for-development' # Django usually provides this already


# dictionary_project/settings.py

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-z*z9-^k!2s_#6(x-j1@*n1m!p@6a7&9b+v_2m(0e-s2r-q2_i6' # <-- Replace with a new, random string


# dictionary_project/settings.py

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', # <-- Add this
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', # <-- Add this
    'django.contrib.messages.middleware.MessageMiddleware', # <-- Add this
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# dictionary_project/settings.py

# ... (rest of your settings) ...

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# dictionary_project/settings.py

# ... (rest of your settings) ...

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/' # <-- Add this line