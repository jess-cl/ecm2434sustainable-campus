
# urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views



urlpatterns = [
    path('', views.announcement_list, name='announcement_list'),
    path('create/', views.create_announcement, name='create_announcement'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

