
# urls.py

from django.urls import path
from . import views
from .views import like_announcement, dislike_announcement

app_name = 'announcements'

urlpatterns = [
    path('', views.announcement_list, name='announcement_list'),
    path('create/', views.create_announcement, name='create_announcement'),
    path('announcement/<int:announcement_id>/like/', like_announcement, name='like_announcement'),
    path('announcement/<int:announcement_id>/dislike/', dislike_announcement, name='dislike_announcement'),

    path('display_event_qr_code/<str:event_code>/', views.display_event_qr_code, name='display_event_qr_code'),
    path('redeem_event_reward/<str:event_code>/', views.redeem_event_reward, name='redeem_event_reward'),
]

