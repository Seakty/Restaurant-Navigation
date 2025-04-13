from django.contrib import admin
from .models import Restaurant, Menu, Feedback

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'cuisine', 'location', 'rating', 'short_description')
    search_fields = ('name', 'cuisine', 'location', 'description')
    list_filter = ('cuisine', 'rating')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'image'),
        }),
        ('Restaurant Information', {
            'fields': ('location', 'google_maps_link', 'cuisine', 'rating'),
        }),
    )
    readonly_fields = ('short_description',)

    def short_description(self, obj):
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
    short_description.short_description = "Description (Short)"


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'price')
    search_fields = ('name', 'restaurant__name', 'description')
    list_filter = ('restaurant',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'restaurant', 'rating', 'created_at')
    list_filter = ('restaurant', 'rating', 'created_at')
    search_fields = ('customer_name', 'restaurant__name', 'comments')

