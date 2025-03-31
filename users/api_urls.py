from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, UserProfileView, 
    BillingInfoView, UpgradeToSellerView, UserStoreView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='api_register'),
    path('login/', LoginView.as_view(), name='api_login'),
    path('logout/', LogoutView.as_view(), name='api_logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('profile/', UserProfileView.as_view(), name='api_profile'),
    path('profile/store/', UserStoreView.as_view(), name='api_user_store'), 
    path('billing/', BillingInfoView.as_view(), name='api_billing'),
    path('upgrade-seller/', UpgradeToSellerView.as_view(), name='api_upgrade_seller'),
]
