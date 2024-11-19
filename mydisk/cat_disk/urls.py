from django.urls import path
from . import views


app_name = "cat_disk"

urlpatterns = [
    path("", views.index, name='index'),
    path("download/", views.download, name="download"),
]