from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin panel configuration
    """
    model = CustomUser

    # Fields to display in user list
    list_display = ['username', 'email', 'first_name', 'last_name', 'age', 'is_staff']

    # Add your custom fields to the admin form
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('age', 'phone_number', 'bio')}),
    )

    # Fields to show when creating a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('age', 'phone_number', 'bio', 'email')}),
    )

# Register the custom user model
admin.site.register(CustomUser, CustomUserAdmin)