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

@api_view(['POST'])
@permission_classes([AllowAny])
def create_superuser(request):
    """
    Creates a Django superuser via API request.
    """
    import os
    import uuid
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    setup_token = os.environ.get('SETUP_TOKEN', str(uuid.uuid4()))
    request_token = request.data.get('setup_token')
    
    if not request_token or request_token != setup_token:
        return Response(
            {"error": "Invalid or missing setup token"},
            status=401
        )
    
    # Get user details from request
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    # Validate input
    if not username or not email or not password:
        return Response(
            {"error": "Username, email and password are required"},
            status=400
        )
    
    if len(password) < 8:
        return Response(
            {"error": "Password must be at least 8 characters long"},
            status=400
        )
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        return Response(
            {"error": f"User with username '{username}' already exists"},
            status=400
        )
    
    if User.objects.filter(email=email).exists():
        return Response(
            {"error": f"User with email '{email}' already exists"},
            status=400
        )
    
    try:
        # Create the superuser
        superuser = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        return Response({
            "success": True,
            "message": f"Superuser '{username}' created successfully",
            "user_id": superuser.id
        })
        
    except Exception as e:
        return Response(
            {"error": f"Failed to create superuser: {str(e)}"},
            status=500
        )
