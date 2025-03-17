from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("estimate/", views.estimate, name="estimate"),  # Add this line
]
