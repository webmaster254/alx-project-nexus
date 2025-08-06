from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from drf_spectacular.openapi import OpenApiTypes
from .serializers import (
    CustomTokenObtainPairSerializer, UserSerializer, UserRegistrationSerializer,
    UserProfileSerializer, UserWithProfileSerializer, PasswordChangeSerializer
)
from .models import UserProfile

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view that returns user data along with tokens.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        tags=['Authentication'],
        summary='Login with email and password',
        description='Authenticate user with email and password to obtain JWT tokens',
        examples=[
            OpenApiExample(
                'Login Example',
                value={
                    'email': 'user@example.com',
                    'password': 'securepassword123'
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                description='Login successful',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                            'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                            'user': {
                                'id': 1,
                                'email': 'user@example.com',
                                'username': 'user@example.com',
                                'first_name': 'John',
                                'last_name': 'Doe',
                                'is_admin': False
                            }
                        }
                    )
                ]
            ),
            401: OpenApiResponse(
                description='Invalid credentials',
                examples=[
                    OpenApiExample(
                        'Invalid Credentials',
                        value={'detail': 'No active account found with the given credentials'}
                    )
                ]
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT token refresh view with additional validation.
    """
    
    @extend_schema(
        tags=['Authentication'],
        summary='Refresh JWT access token',
        description='Use refresh token to obtain a new access token',
        examples=[
            OpenApiExample(
                'Refresh Token Example',
                value={
                    'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                description='Token refreshed successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                            'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                        }
                    )
                ]
            ),
            401: OpenApiResponse(
                description='Invalid or expired refresh token',
                examples=[
                    OpenApiExample(
                        'Invalid Token',
                        value={'detail': 'Token is invalid or expired', 'code': 'token_not_valid'}
                    )
                ]
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Alternative login view using email and password.
    Returns JWT tokens and user information.
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {'error': 'Email and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=email, password=password)
    
    if user is not None:
        if user.is_active:
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'User account is disabled'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
    else:
        return Response(
            {'error': 'Invalid email or password'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@extend_schema(
    tags=['Authentication'],
    summary='Logout user',
    description='Blacklist refresh token to logout user',
    examples=[
        OpenApiExample(
            'Logout Example',
            value={
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
            },
            request_only=True
        )
    ],
    responses={
        200: OpenApiResponse(
            description='Logout successful',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={'message': 'Successfully logged out'}
                )
            ]
        ),
        400: OpenApiResponse(
            description='Invalid request',
            examples=[
                OpenApiExample(
                    'Missing Token',
                    value={'error': 'Refresh token is required'}
                ),
                OpenApiExample(
                    'Invalid Token',
                    value={'error': 'Invalid token'}
                )
            ]
        )
    }
)
@api_view(['POST'])
def logout_view(request):
    """
    Logout view that blacklists the refresh token.
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'message': 'Successfully logged out'}, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Refresh token is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except TokenError:
        return Response(
            {'error': 'Invalid token'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    tags=['Authentication'],
    summary='Verify JWT token',
    description='Verify if a JWT token is valid and not expired',
    examples=[
        OpenApiExample(
            'Token Verification Example',
            value={
                'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
            },
            request_only=True
        )
    ],
    responses={
        200: OpenApiResponse(
            description='Token is valid',
            examples=[
                OpenApiExample(
                    'Valid Token',
                    value={'valid': True, 'message': 'Token is valid'}
                )
            ]
        ),
        401: OpenApiResponse(
            description='Token is invalid or expired',
            examples=[
                OpenApiExample(
                    'Invalid Token',
                    value={'valid': False, 'error': 'Token is invalid or expired'}
                )
            ]
        ),
        400: OpenApiResponse(
            description='Token not provided',
            examples=[
                OpenApiExample(
                    'Missing Token',
                    value={'error': 'Token is required'}
                )
            ]
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_token_view(request):
    """
    View to verify if a JWT token is valid.
    """
    token = request.data.get('token')
    
    if not token:
        return Response(
            {'error': 'Token is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Try to decode the token
        from rest_framework_simplejwt.tokens import UntypedToken
        UntypedToken(token)
        return Response(
            {'valid': True, 'message': 'Token is valid'}, 
            status=status.HTTP_200_OK
        )
    except TokenError:
        return Response(
            {'valid': False, 'error': 'Token is invalid or expired'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@extend_schema(
    tags=['Authentication'],
    summary='Register new user account',
    description='Create a new user account with email and password',
    request=UserRegistrationSerializer,
    examples=[
        OpenApiExample(
            'Registration Example',
            value={
                'email': 'newuser@example.com',
                'password': 'securepassword123',
                'password_confirm': 'securepassword123',
                'first_name': 'John',
                'last_name': 'Doe'
            },
            request_only=True
        )
    ],
    responses={
        201: OpenApiResponse(
            description='User registered successfully',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        'message': 'User registered successfully',
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'user': {
                            'id': 2,
                            'email': 'newuser@example.com',
                            'username': 'newuser@example.com',
                            'first_name': 'John',
                            'last_name': 'Doe',
                            'is_admin': False,
                            'profile': {
                                'phone_number': None,
                                'bio': None,
                                'location': None,
                                'experience_years': None
                            }
                        }
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description='Validation error',
            examples=[
                OpenApiExample(
                    'Validation Error',
                    value={
                        'email': ['User with this email already exists.'],
                        'password': ['This password is too common.']
                    }
                )
            ]
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    User registration view that creates a new user account.
    Returns JWT tokens and user information upon successful registration.
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        user_serializer = UserWithProfileSerializer(user)
        
        return Response({
            'message': 'User registered successfully',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    summary='Get or update user profile',
    description='Retrieve or update the authenticated user\'s profile information',
    request=UserProfileSerializer,
    examples=[
        OpenApiExample(
            'Profile Update Example',
            value={
                'first_name': 'John',
                'last_name': 'Doe',
                'phone_number': '+1234567890',
                'bio': 'Experienced software developer',
                'location': 'San Francisco, CA',
                'experience_years': 5
            },
            request_only=True
        )
    ],
    responses={
        200: OpenApiResponse(
            description='Profile retrieved or updated successfully',
            examples=[
                OpenApiExample(
                    'Profile Response',
                    value={
                        'id': 1,
                        'email': 'user@example.com',
                        'username': 'user@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'is_admin': False,
                        'profile': {
                            'phone_number': '+1234567890',
                            'bio': 'Experienced software developer',
                            'location': 'San Francisco, CA',
                            'experience_years': 5
                        }
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description='Validation error',
            examples=[
                OpenApiExample(
                    'Validation Error',
                    value={
                        'phone_number': ['Enter a valid phone number.'],
                        'experience_years': ['Ensure this value is greater than or equal to 0.']
                    }
                )
            ]
        ),
        401: OpenApiResponse(
            description='Authentication required',
            examples=[
                OpenApiExample(
                    'Unauthorized',
                    value={'detail': 'Authentication credentials were not provided.'}
                )
            ]
        )
    }
)
@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    User profile view for retrieving and updating user profile information.
    """
    user = request.user
    
    if request.method == 'GET':
        # Get user profile with all information
        serializer = UserWithProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method in ['PUT', 'PATCH']:
        # Update user profile
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = UserProfile.objects.create(user=user)
        
        # Update user basic information if provided
        user_data = {}
        for field in ['first_name', 'last_name', 'username']:
            if field in request.data:
                user_data[field] = request.data[field]
        
        if user_data:
            user_serializer = UserSerializer(user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Update profile information
        profile_serializer = UserProfileSerializer(
            profile, 
            data=request.data, 
            partial=request.method == 'PATCH'
        )
        
        if profile_serializer.is_valid():
            profile_serializer.save()
            
            # Return updated user with profile
            updated_user_serializer = UserWithProfileSerializer(user)
            return Response(updated_user_serializer.data, status=status.HTTP_200_OK)
        
        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    summary='Change user password',
    description='Change the authenticated user\'s password',
    request=PasswordChangeSerializer,
    examples=[
        OpenApiExample(
            'Password Change Example',
            value={
                'old_password': 'currentpassword123',
                'new_password': 'newsecurepassword456',
                'new_password_confirm': 'newsecurepassword456'
            },
            request_only=True
        )
    ],
    responses={
        200: OpenApiResponse(
            description='Password changed successfully',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={'message': 'Password changed successfully'}
                )
            ]
        ),
        400: OpenApiResponse(
            description='Validation error',
            examples=[
                OpenApiExample(
                    'Validation Error',
                    value={
                        'old_password': ['Old password is incorrect.'],
                        'new_password': ['This password is too common.']
                    }
                )
            ]
        ),
        401: OpenApiResponse(
            description='Authentication required',
            examples=[
                OpenApiExample(
                    'Unauthorized',
                    value={'detail': 'Authentication credentials were not provided.'}
                )
            ]
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    View for changing user password.
    """
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response(
            {'message': 'Password changed successfully'}, 
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    summary='Get current user information',
    description='Retrieve the authenticated user\'s information including profile data',
    responses={
        200: OpenApiResponse(
            description='User information retrieved successfully',
            examples=[
                OpenApiExample(
                    'User Info Response',
                    value={
                        'id': 1,
                        'email': 'user@example.com',
                        'username': 'user@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'is_admin': False,
                        'profile': {
                            'phone_number': '+1234567890',
                            'bio': 'Experienced software developer',
                            'location': 'San Francisco, CA',
                            'experience_years': 5
                        }
                    }
                )
            ]
        ),
        401: OpenApiResponse(
            description='Authentication required',
            examples=[
                OpenApiExample(
                    'Unauthorized',
                    value={'detail': 'Authentication credentials were not provided.'}
                )
            ]
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info_view(request):
    """
    View to get current user information.
    """
    serializer = UserWithProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Authentication'],
    summary='Deactivate user account',
    description='Deactivate the authenticated user\'s account (soft delete)',
    responses={
        200: OpenApiResponse(
            description='Account deactivated successfully',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={'message': 'Account deactivated successfully'}
                )
            ]
        ),
        401: OpenApiResponse(
            description='Authentication required',
            examples=[
                OpenApiExample(
                    'Unauthorized',
                    value={'detail': 'Authentication credentials were not provided.'}
                )
            ]
        )
    }
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deactivate_account_view(request):
    """
    View to deactivate user account (soft delete).
    """
    user = request.user
    user.is_active = False
    user.save()
    
    return Response(
        {'message': 'Account deactivated successfully'}, 
        status=status.HTTP_200_OK
    )