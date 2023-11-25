from django.urls import path
from . import views


urlpatterns = [
    # api endpoint
    path('createvideo/',views.create)
]