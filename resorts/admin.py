from django.contrib import admin
from .models import UserProfile, Resort, Booking

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_resort_owner', 'phone')
    list_filter = ('is_resort_owner',)
    search_fields = ('user__username', 'phone', 'address')
    raw_id_fields = ('user',)

@admin.register(Resort)
class ResortAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'location', 'price_per_night', 'is_available', 'created_at')
    list_filter = ('is_available', 'created_at')
    search_fields = ('name', 'location', 'description')
    raw_id_fields = ('owner',)
    list_editable = ('is_available', 'price_per_night')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'owner', 'description', 'location')
        }),
        ('Pricing and Availability', {
            'fields': ('price_per_night', 'is_available')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'resort', 'check_in_date', 'check_out_date', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'check_in_date', 'check_out_date', 'created_at')
    search_fields = ('user__username', 'resort__name', 'rejection_reason')
    raw_id_fields = ('user', 'resort')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'resort', 'check_in_date', 'check_out_date', 'total_price')
        }),
        ('Status', {
            'fields': ('status', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('user', 'resort', 'check_in_date', 'check_out_date', 'total_price')
        return self.readonly_fields
