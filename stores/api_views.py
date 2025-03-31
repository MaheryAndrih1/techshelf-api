from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Store, StoreTheme, Rating
from .serializers import StoreSerializer, StoreCreateSerializer, StoreThemeSerializer, RatingSerializer
import logging
import traceback

# Configure logger
logger = logging.getLogger(__name__)

class StoreListView(generics.ListAPIView):
    """List all stores with optional filtering"""
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['store_name', 'subdomain_name']

class StoreDetailView(generics.RetrieveAPIView):
    """Get details of a specific store by subdomain"""
    serializer_class = StoreSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'subdomain_name'
    lookup_url_kwarg = 'subdomain'
    queryset = Store.objects.all()

class StoreCreateView(APIView):
    """Create a new store (requires seller role)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Check if user already has a store
            user = request.user
            if hasattr(user, 'store'):
                return Response(
                    {'error': 'You already have a store. You cannot create multiple stores.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Extract data from request
            store_name = request.data.get('store_name')
            subdomain_name = request.data.get('subdomain_name')
            
            if not store_name:
                return Response(
                    {'error': 'Store name is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update user to seller if not already
            if user.role != 'SELLER':
                user.role = 'SELLER'
                user.save()
                
            # Create store manually instead of using serializer
            store = Store(
                store_name=store_name,
                subdomain_name=subdomain_name if subdomain_name else None,
                user=user
            )
            store.save() 

            primary_color = request.data.get('primary_color', '#3498db')
            secondary_color = request.data.get('secondary_color', '#2ecc71')
            font = request.data.get('font', 'Roboto')
            
            # Create theme manually
            theme = StoreTheme(
                theme_id=f"theme_{store.store_id}",
                primary_color=primary_color,
                secondary_color=secondary_color,
                font=font
            )
            
            if 'logo_url' in request.FILES:
                theme.logo_url = request.FILES['logo_url']
                print(f"Logo image received: {theme.logo_url}")
            
            if 'banner_url' in request.FILES:
                theme.banner_url = request.FILES['banner_url']
                print(f"Banner image received: {theme.banner_url}")
                
            theme.save()
            
            store.theme = theme
            store.save()

            serializer = StoreSerializer(store)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Store creation failed: {str(e)}")
            logger.error(traceback.format_exc()) 
            
            return Response(
                {'error': f'Failed to create store: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StoreUpdateView(generics.UpdateAPIView):
    """Update store details if owner"""
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'subdomain_name'
    lookup_url_kwarg = 'subdomain'
    
    def get_queryset(self):
        return Store.objects.filter(user=self.request.user)

class StoreThemeView(generics.RetrieveUpdateAPIView):
    """Get or update a store theme if owner"""
    serializer_class = StoreThemeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        store = get_object_or_404(Store, 
                                 subdomain_name=self.kwargs['subdomain'],
                                 user=self.request.user)
        
        theme, created = StoreTheme.objects.get_or_create(
            id=store.theme.id if store.theme else None,
            defaults={
                'theme_id': f"theme_{store.store_id}",
                'primary_color': '#3498db',
                'secondary_color': '#2ecc71',
                'font': 'Roboto'
            }
        )
        
        if created:
            store.theme = theme
            store.save()
            
        return theme

class StoreRatingListView(generics.ListAPIView):
    """List all ratings for a specific store"""
    serializer_class = RatingSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        store = get_object_or_404(Store, subdomain_name=self.kwargs['subdomain'])
        return Rating.objects.filter(store=store).order_by('-timestamp')

class StoreRatingCreateView(APIView):
    """Create a rating for a store"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, subdomain):
        store = get_object_or_404(Store, subdomain_name=subdomain)
        
        if store.user == request.user:
            return Response(
                {'detail': 'You cannot rate your own store.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = RatingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if the user already rated this store
        existing_rating = Rating.objects.filter(user=request.user, store=store).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.score = serializer.validated_data['score']
            existing_rating.comment = serializer.validated_data.get('comment', '')
            existing_rating.save()
            
            # Return updated rating data
            return Response(RatingSerializer(existing_rating).data, status=status.HTTP_200_OK)
        else:
            # Create new rating
            rating = serializer.save(
                user=request.user,
                store=store,
                rating_id=f"rating_{request.user.id}_{store.store_id}"
            )
            
            return Response(RatingSerializer(rating).data, status=status.HTTP_201_CREATED)
