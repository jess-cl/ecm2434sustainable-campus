from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.first_page, name='first_page'),  # First page the website should lead to when accessed
    path('map/', views.map, name='map'),
    path('forest/', views.forest, name='forest'),
    path('forest/save', views.save_forest, name='save_forest'),
    path('forest/save_customisations', views.save_customisations, name='save_customisations'),
    path('forest/update_forest_on_page', views.update_forest_on_page, name='update_forest_on_page'),
    path('forest/update_inventory_on_forest', views.update_inventory_on_forest, name='update_inventory_on_forest'),
    path('forest/handle_recycling', views.handle_recycling, name='handle_recycling'),
    path('forest/get_recycled_count', views.get_recycled_count, name='get_recycled_count'),
    path('forest/add_tokens', views.add_tokens, name='add_tokens'),
    path('forest/update_forest_on_page', views.update_forest_on_page, name='update_forest_on_page'),
    path('forest/remove_from_inv', views.remove_from_inv, name='remove_from_inv'),
    path('forest/use_consumable', views.use_consumable, name='use_consumable'),
    path('map/claim_blue_marker', views.claim_blue_marker, name='claim_blue_marker'),
    path('map/claim_red_marker', views.claim_red_marker, name='claim_red_marker'),
    path('map/claim_green_marker', views.claim_green_marker, name='claim_green_marker'),
    path('map/update_inv_on_page', views.update_inv_on_page, name='update_inv_on_page')
]
