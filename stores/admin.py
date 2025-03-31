from django.contrib import admin
from .models import Store, StoreTheme, Rating

class StoreAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'subdomain_name', 'user', 'created_at')
    search_fields = ('store_name', 'subdomain_name', 'user__username')
    prepopulated_fields = {'subdomain_name': ('store_name',)}

class StoreThemeAdmin(admin.ModelAdmin):
    list_display = ('theme_id', 'primary_color', 'secondary_color', 'font')
    search_fields = ('theme_id',)

class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'store', 'score', 'timestamp')
    list_filter = ('score',)
    search_fields = ('user__username', 'store__store_name', 'comment')
    date_hierarchy = 'timestamp'

admin.site.register(Store, StoreAdmin)
admin.site.register(StoreTheme, StoreThemeAdmin)
admin.site.register(Rating, RatingAdmin)
