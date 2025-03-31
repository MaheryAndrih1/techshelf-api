from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list_view, name='list'),
    path('create/', views.create_product_view, name='create'),
    path('<str:product_id>/', views.product_detail_view, name='detail'),
    path('<str:product_id>/edit/', views.edit_product_view, name='edit'),
    path('<str:product_id>/like/', views.like_product_view, name='like'),
    path('category/<str:category>/', views.product_category_view, name='category'),
]
