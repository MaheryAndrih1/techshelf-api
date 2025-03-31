from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """API health check endpoint"""
    return Response({
        'status': 'ok',
        'message': 'Hello Mahery'
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def api_debug_view(request):
    """Debug endpoint to check API configuration"""
    from django.conf import settings
    
    # Return useful debugging information
    debug_info = {
        'DEBUG': settings.DEBUG,
        'INSTALLED_APPS': settings.INSTALLED_APPS,
        'REST_FRAMEWORK_SETTINGS': getattr(settings, 'REST_FRAMEWORK', {}),
        'MIDDLEWARE': settings.MIDDLEWARE,
        'DATABASES': {
            name: {'ENGINE': details['ENGINE']} 
            for name, details in settings.DATABASES.items()
        },
        'AUTHENTICATION_BACKENDS': settings.AUTHENTICATION_BACKENDS,
    }
    
    return Response(debug_info)
