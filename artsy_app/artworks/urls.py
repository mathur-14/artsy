from django.urls import path
from . import views

urlpatterns = [
    path('get-token/', views.get_token, name='get_token'),
    path('put-artworks/', views.put_artworks, name='put_artworks'),
    path('get-artists/', views.get_artists, name='get_artists'),
    path('get-paginated-artworks/', views.get_paginated_artworks, name='get_paginated_artworks'),
    path('get-artwork-id/<str:id>/', views.get_artwork_by_id, name='get_artwork_by_id'),
    path('get-artworks-category/<str:category>/', views.get_artwork_by_category, name='get_artwork_by_category'),
    path('get-artworks-by-artist/<str:artist_id>', views.get_artworks_by_artist, name='get_artworks_by_artist'),
    path('get-artworks-by-period/<str:period>', views.get_artworks_by_period, name='get_artworks_by_period'),
    path('get-categories/', views.get_categories, name='get_categories'),
    path('put_paginated_genes/', views.put_paginated_genes, name='put_paginated_genes'),
    path('put_genes/', views.put_genes, name='put_genes'),
    path('genes_rows/', views.genes_rows, name='genes_rows'),
    path('artworks_words/', views.artworks_words, name='artworks_words'),
    path('price_data/', views.price_data, name='price_data'),
    path('favourites_data/', views.favourites_data, name='favourites_data'),
    path('investments_data/', views.investments_data, name='investments_data'),
    path('recommended_favourites/', views.recommended_favourites, name='recommended_favourites'),
    path('recommended_investments/', views.recommended_investments, name='recommended_investments'),
    path('investments_data/', views.investments_data, name='investments_data'),
    path('keywords_search/', views.keywords_search, name='keywords_search'),
]
