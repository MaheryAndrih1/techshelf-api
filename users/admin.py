from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, BillingInfo

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

class BillingInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_number', 'expiry_date')
    search_fields = ('user__username', 'user__email')

admin.site.register(User, CustomUserAdmin)
admin.site.register(BillingInfo, BillingInfoAdmin)
