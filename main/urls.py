from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.first_page, name='first_page'),  # First page the website should lead to when accessed
    path('map/', views.map, name='map'),
    path('forest/', views.forest, name='forest'),
    # main/urls.py
]
