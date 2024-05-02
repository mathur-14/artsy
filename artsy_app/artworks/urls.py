from django.urls import path
from . import views

urlpatterns = [
    path('get-token/', views.get_token, name='get_token'),
    path('put-artworks/', views.put_artworks, name='put_artworks'),
    path('get-artists/', views.get_artists, name='get_artists'),
    path('get-paginated-artworks/', views.get_paginated_artworks, name='get_paginated_artworks'),
    path('get-artwork/<str:id>/', views.get_artwork, name='get_artwork'),
    # path('put-artists/', views.put_artists, name='put_artists'),
]
