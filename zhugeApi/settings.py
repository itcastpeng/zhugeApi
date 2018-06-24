"""
Django settings for zhugeApi project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'deb!gj80!pstwg39(sxl4#e2t+m1&)j&kx2nh10u5s_low*%vw'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'wendaku',
    'ribao',
    'zhugedanao',
    'zhugeleida',
    'zhugeproject'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 跨域增加忽略
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    '*'
)

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)

CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Pragma',
)

ROOT_URLCONF = 'zhugeApi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'zhugeApi.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'wendaku': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wendaku',
        'HOST': 'wendaku',
        'PORT': '3306',
        'USER': 'wendaku',
        'PASSWORD': 'wendaku'
    },

    'ribao': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ribao',
        'HOST': 'ribao',
        'PORT': '3306',
        'USER': 'ribao',
        'PASSWORD': 'ribao'
    },
    'zhugedanao': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'zhugedanao',
        'HOST': 'zhugedanao',
        'PORT': '3306',
        'USER': 'zhugedanao',
        'PASSWORD': 'zhugedanao'
    },
    'zhugeleida': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'zhugeleida',
        'HOST': 'zhugeleida',
        'PORT': '3306',
        'USER': 'zhugeleida',
        'PASSWORD': 'zhugeleida',
        'OPTIONS': {
                    'init_command': 'SET storage_engine=INNODB',
                },
            },
    'zhugeproject': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'zhugeproject',
            'HOST': 'zhugeproject',
            'PORT': '3306',
            'USER': 'zhugeproject',
            'PASSWORD': 'zhugeproject'
        }
}

DATABASE_ROUTERS = ['wendaku.database_router.DatabaseAppsRouter']
DATABASE_APPS_MAPPING = {
    # example:
    # 'app_name':'database_name',
    'wendaku': 'wendaku',
    'ribao': 'ribao',
    'zhugedanao': 'zhugedanao',
    'zhugeleida': 'zhugeleida',
    'zhugeproject':'zhugeproject',
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

# LANGUAGE_CODE = 'en-us'
#
# TIME_ZONE = 'UTC'
#
# USE_I18N = True
#
# USE_L10N = True
#
# USE_TZ = True


USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/statics/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'statics')]
