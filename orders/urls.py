from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<str:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/remove/<str:product_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('cart/update/<str:product_id>/', views.update_cart_quantity_view, name='update_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/shipping/', views.shipping_info_view, name='shipping'),
    path('checkout/payment/', views.payment_view, name='payment'),
    path('orders/', views.order_list_view, name='list'),
    path('orders/<str:order_id>/', views.order_detail_view, name='detail'),
    path('promotions/apply/', views.apply_promotion_view, name='apply_promotion'),
]
