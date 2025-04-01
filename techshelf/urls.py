from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import health_check, api_debug_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('stores/', include('stores.api_urls')),  # Make sure this line exists
        path('health/', health_check, name='api_health_check'),
        path('debug/', api_debug_view, name='api_debug'),
        path('users/', include('users.api_urls')),
        path('products/', include('products.api_urls')),
        path('orders/', include('orders.api_urls')),
        path('notifications/', include('notifications.api_urls')),
    ])),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
