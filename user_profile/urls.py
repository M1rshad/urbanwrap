from django.urls import path
from . import views
urlpatterns = [
    path('dashbord/', views.dashboard, name='dashboard'),
]