from django.urls import path
from .api_views import (
    StoreListView, StoreDetailView, StoreCreateView, StoreUpdateView,
    StoreThemeView, StoreRatingListView, StoreRatingCreateView
)

urlpatterns = [
    path('', StoreListView.as_view(), name='api_store_list'),
    path('create/', StoreCreateView.as_view(), name='api_store_create'),
    path('<str:subdomain>/', StoreDetailView.as_view(), name='api_store_detail'),
    path('<str:subdomain>/update/', StoreUpdateView.as_view(), name='api_store_update'),
    path('<str:subdomain>/theme/', StoreThemeView.as_view(), name='api_store_theme'),
    path('<str:subdomain>/ratings/', StoreRatingListView.as_view(), name='api_store_ratings'),
    path('<str:subdomain>/rate/', StoreRatingCreateView.as_view(), name='api_store_rate'),
]
