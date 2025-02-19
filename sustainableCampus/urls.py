"""
URL configuration for sustainableCampus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
import sustainableCampus.views as views

urlpatterns = [
    path("main/", include("main.urls")),
    path('admin/', admin.site.urls),
    path('announcements/', include('announcements.urls')),  # Include the URLs for the social app

    path('', views.home, name='home')
]
