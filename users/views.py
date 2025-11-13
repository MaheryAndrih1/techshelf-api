from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import BillingInfo
from .forms import RegistrationForm, ProfileEditForm, BillingInfoForm
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserRegisterSerializer, BillingInfoSerializer
from stores.models import Store
from stores.serializers import StoreSerializer

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # For debugging
        print(f"Attempting login with email: {email}")
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            
            # Check for next parameter
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('landing:home')
        else:
            messages.error(request, 'Invalid email or password.')
            
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('landing:home')

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('landing:home')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'users/profile.html')

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('users:profile')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def billing_info_view(request):
    if request.method == 'POST':
        form = BillingInfoForm(request.POST, instance=request.user.billinginfo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your billing information has been updated.')
            return redirect('users:profile')
    else:
        form = BillingInfoForm(instance=request.user.billinginfo)
    return render(request, 'users/billing.html', {'form': form})

@login_required
def upgrade_to_seller_view(request):
    if request.method == 'POST':
        request.user.upgrade_to_seller()
        messages.success(request, 'Your account has been upgraded to seller.')
        return redirect('users:profile')
    return render(request, 'users/upgrade_seller.html')

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer
    
    def create(self, request, *args, **kwargs):
        print("Registration request data:", request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Debug log to see what's being sent
        print(f"Login attempt with email: {email}, password: {password[:1]}***")
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        
        return Response({'error': 'Invalid credentials. Please check your email and password.'}, 
                       status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class BillingInfoView(generics.RetrieveUpdateAPIView):
    serializer_class = BillingInfoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        billing_info, created = BillingInfo.objects.get_or_create(user=self.request.user)
        return billing_info

class UpgradeToSellerView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        if user.role == 'SELLER':
            return Response({'message': 'User is already a seller'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.role = 'SELLER'
        user.save()
        
        return Response({'message': 'Account upgraded to seller successfully'}, status=status.HTTP_200_OK)

class UserStoreView(APIView):
    """Get the store associated with the current user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            store = Store.objects.get(user=request.user)
            serializer = StoreSerializer(store)
            return Response(serializer.data)
        except Store.DoesNotExist:
            return Response(
                {'error': 'You do not have a store yet'}, 
                status=status.HTTP_404_NOT_FOUND
            )
