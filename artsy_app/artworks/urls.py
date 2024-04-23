from django.urls import path
from . import views

urlpatterns = [
    path('get-token/', views.get_token, name='get_token'),
    path('get-artworks/', views.get_artworks, name='get_artworks'),
    path('put-artworks/', views.put_artworks, name='put_artworks'),
]
