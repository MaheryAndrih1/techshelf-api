from django.urls import path
from .api_views import (
    CartView, CartAddItemView, CartRemoveItemView, CartUpdateItemView,
    CheckoutView, OrderListView, OrderDetailView, OrderCancelView,
    ApplyPromotionView, SellerOrderListView, SellerOrderDetailView,
    SellerOrderUpdateStatusView, MergeCartView
)

urlpatterns = [
    path('cart/', CartView.as_view(), name='api_cart'),
    path('cart/add/', CartAddItemView.as_view(), name='api_cart_add'),
    path('cart/remove/<str:product_id>/', CartRemoveItemView.as_view(), name='api_cart_remove'),
    path('cart/update/<str:product_id>/', CartUpdateItemView.as_view(), name='api_cart_update'),
    path('checkout/', CheckoutView.as_view(), name='api_checkout'),
    path('orders/', OrderListView.as_view(), name='api_order_list'),
    path('seller-orders/', SellerOrderListView.as_view(), name='api_seller_order_list'),
    path('orders/<str:order_id>/', OrderDetailView.as_view(), name='api_order_detail'),
    path('orders/<str:order_id>/cancel/', OrderCancelView.as_view(), name='api_order_cancel'),
    path('promotions/apply/', ApplyPromotionView.as_view(), name='api_apply_promotion'),
    path('seller-orders/<str:order_id>/', SellerOrderDetailView.as_view(), name='api_seller_order_detail'),
    path('seller-orders/<str:order_id>/update-status/', SellerOrderUpdateStatusView.as_view(), name='api_seller_order_update_status'),
    path('cart/merge/', MergeCartView.as_view(), name='merge-cart'),
]