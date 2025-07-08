from django.urls import path
from . import views
from .api.api import api
urlpatterns = [
    path("", views.index, name="index"),
    path("index/", views.index, name="index"),
    path("api/", api.urls)
]
