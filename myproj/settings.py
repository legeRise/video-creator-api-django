"""
Django settings for myproj project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
import os  # had to use
load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^p3a+@2pedfabh-5i&7bu+j7-mh%v&&i@+1x-ww!0kltd7%@&#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False  # when false run collectstatic command (using whitenoise or whatever)

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'webcreatorApp',
    'corsheaders'

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',      # this was added
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


CORS_ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "https://ytshortmaker-frontend.onrender.com" # no trailing slashes, cause it becomes path and paths are not allowed
]


ROOT_URLCONF = 'myproj.urls'

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

WSGI_APPLICATION = 'myproj.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/


STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# the video creation process takes place in media dir locally so it has to be here even in production
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


MEDIA_URL = 'media/'


FONT_BASE_DIR = os.path.join(BASE_DIR,'functionality','fonts')


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ai model

GEMINI_MODEL = 'gemini-pro'
GEMINI_API = os.getenv("GEMINI_API")

PROMPT = f"""I am going to provide you a title and you have to find the corresponding items against it and make 
        two lists of them  one for the actual 'imagesearch' and the other for the 
        'overlay text'
        So for example if i give you   title :  top 5 oceans in the world 
        you will reply with and remember only this response nothing else
        
        Image_Keywords: Pacific Ocean, Atlantic Ocean, Indian Ocean, Southern Ocean, Arctic Ocean
        Display_Keywords: Pacific Ocean, Atlantic Ocean, Indian Ocean, Southern Ocean, Arctic Ocean

        REMEMBER SAME AS THIS NO EXTRA CHARACTER, NOTHING!

        ALSO, THE NUMBER OF KEYWORDS SHOULD MEET THE NUMBER REQUESTED IN TITLE  for example if he said 'Top 7' then
        seven keywords(image and display both) and so on!
        
        where in the 'Image_Keywords  you have to add extra tags that will ensure that on searching the keyword
        the images of that item(say pacific ocean) will pop up and so on, while in the display keyword  you have
        to write short an proper titles  that would look nice as an overlay so for image of 'pacific ocean'  overlay
        text of  'Pacific Ocean'  capitalized looks beautiful

        ALSO REMEMBER, IF YOUR RESPONSE WAS EXACT TO THE POINT AND THEN I REQUEST THE SAME TITLE AGAIN AND AGAIN 
        YOU HAVE TO RESPOND WITH SAME RESPOPNSE(PROVIDED IT WAS EXACT ON SPOT) DON'T JUST CHANGE YOUR RESPONSE JUST 
        BECAUSE IT WAS REQUESTED AGAIN AND AGAIN
        
        follow the same instructions for  this Title : """



#google drive upload configurations

DRIVE_PARENT_FOLDER_ID = os.getenv("DRIVE_PARENT_FOLDER_ID")

# by default( in local environment) it will pick the file from BASE_DIR, while in case of docker container '-e' tag can be used
SERVICE_ACCOUNT_FILE =  os.getenv('SERVICE_ACCOUNT_FILE', default=os.path.join(BASE_DIR,'service_account_file.json')) 
