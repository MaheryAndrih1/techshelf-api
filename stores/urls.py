from django.urls import path
from . import views

app_name = 'stores'

urlpatterns = [
    path('', views.store_list_view, name='list'),
    path('create/', views.create_store_view, name='create'),
    path('<slug:subdomain>/', views.store_detail_view, name='detail'),
    path('<slug:subdomain>/edit/', views.edit_store_view, name='edit'),
    path('<slug:subdomain>/theme/', views.store_theme_view, name='theme'),
    path('<slug:subdomain>/ratings/', views.store_ratings_view, name='ratings'),
    path('<slug:subdomain>/rate/', views.rate_store_view, name='rate'),
]
