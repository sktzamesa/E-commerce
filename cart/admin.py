from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username',)
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)
