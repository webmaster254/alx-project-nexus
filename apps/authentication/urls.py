"""
Authentication app URLs
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from . import views

app_name = 'authentication'

urlpatterns = [
    # JWT Token endpoints
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Authentication endpoints
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify/', views.verify_token_view, name='verify_token'),
    
    # Profile management endpoints
    path('profile/', views.profile_view, name='profile'),
    path('user/', views.user_info_view, name='user_info'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('deactivate/', views.deactivate_account_view, name='deactivate_account'),
]