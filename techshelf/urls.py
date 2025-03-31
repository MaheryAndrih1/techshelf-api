from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import health_check, api_debug_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/health/', health_check, name='api_health_check'),
    path('api/debug/', api_debug_view, name='api_debug'),
    path('api/users/', include('users.api_urls')),
    path('api/stores/', include('stores.api_urls')),
    path('api/products/', include('products.api_urls')),
    path('api/orders/', include('orders.api_urls')),
    path('api/notifications/', include('notifications.api_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
