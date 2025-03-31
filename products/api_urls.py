from django.urls import path
from .api_views import (
    ProductListView, ProductDetailView, ProductCreateView,
    ProductUpdateView, ProductLikeView, CategoryProductsView, 
    UserLikedProductsView, get_user_liked_products
)

urlpatterns = [
    path('', ProductListView.as_view(), name='api_product_list'),
    path('create/', ProductCreateView.as_view(), name='api_product_create'),
    path('<str:product_id>/', ProductDetailView.as_view(), name='api_product_detail'),
    path('<str:product_id>/update/', ProductUpdateView.as_view(), name='api_product_update'),
    path('<str:product_id>/like/', ProductLikeView.as_view(), name='api_product_like'),
    path('category/<str:category>/', CategoryProductsView.as_view(), name='api_product_category'),
    path('liked/', UserLikedProductsView.as_view(), name='api_user_liked_products'),
    path('user/liked/', get_user_liked_products, name='user-liked-products'),
]
