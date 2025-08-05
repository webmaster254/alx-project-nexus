from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'phone_number', 'bio', 'location', 'website', 
        'linkedin_url', 'github_url', 'skills', 'experience_years'
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with profile inline."""
    inlines = (UserProfileInline,)
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_admin', 'is_staff', 'date_joined')
    list_filter = ('is_admin', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('username', 'first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_admin'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model."""
    list_display = ('user', 'phone_number', 'location', 'experience_years', 'created_at')
    list_filter = ('experience_years', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'location')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('User Information'), {'fields': ('user',)}),
        (_('Contact Information'), {'fields': ('phone_number', 'location', 'website')}),
        (_('Social Links'), {'fields': ('linkedin_url', 'github_url')}),
        (_('Professional Information'), {'fields': ('bio', 'skills', 'experience_years', 'resume')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
