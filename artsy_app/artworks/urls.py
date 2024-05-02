from django.urls import path
from . import views

urlpatterns = [
    path('get-token/', views.get_token, name='get_token'),
    path('put-artworks/', views.put_artworks, name='put_artworks'),
    path('get-artists/', views.get_artists, name='get_artists'),
    path('get-paginated-artworks/', views.get_paginated_artworks, name='get_paginated_artworks'),
    path('get-artwork-id/<str:id>/', views.get_artwork_by_id, name='get_artwork_by_id'),
    path('get-artworks-category/<str:category>/', views.get_artwork_by_category, name='get_artwork_by_category'),
    path('get-artists/', views.get_artists, name='get_artists'),
    path('get-artworks-by-artist/<str:artist_id>', views.get_artworks_by_artist, name='get_artworks_by_artist'),
    path('get-categories/', views.get_categories, name='get_categories'),
]
