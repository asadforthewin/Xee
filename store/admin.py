from typing import Any
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Count
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models

class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'
    
    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [('<10', 'Low')]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value () == '<10':
            return queryset.filter(inventory__lt=10)   
        
class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ['thumbnail']

    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html(f'<img src= "{instance.image.url}" class = "thumbnail" />')
        return ' '

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    actions = ['clear_inventory']
    prepopulated_fields = {
        'slug' : ['title'] }
    autocomplete_fields = ['collection']
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_per_page = 10
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_select_related = ['collection']
    search_fields = ['title']

    
    def collection_title(self, product):
        return product.collection.title
    
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'ok'
    
    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory = 0)
        self.message_user(request, 
                          f'{updated_count} products were successfully updated ')
        
    class Media:
        css = {
            'all': ['store/styles.css']
        }
        

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']
    
    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url= reverse("admin:store_product_changelist") + '?' + urlencode({
            'collection__id': str(collection.id)
        })
        return format_html('<a href="{}">{}</a>', url,  collection.products_count)
    
    def get_queryset(self, request):
        return super().get_queryset(request). annotate(
            products_count = Count('products')
        )
        

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'orders']
    autocomplete_fields = ['user']
    list_editable = ['membership']
    list_per_page = 10
    list_select_related = ['user']
    ordering = ['user__first_name' , 'user__last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']
    
    def orders(self, customer):
        url = reverse('admin:store_order_changelist') + '?' + urlencode({"customer__id":str(customer.id)})
         
        return format_html('<a href="{}">{}</a>', url, customer.orders)
        
        
    
    def get_queryset(self, request):
        return super().get_queryset(request). annotate(
            orders = Count('order')
        )
        
        
class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    max_num = 10
    min_num = 1
    model = models.OrderItem
    
@admin.register(models.Order) 
class OrderAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['id', 'placed_at', 'customer'] 
    list_select_related = ['customer']
    inlines = [OrderItemInline]
    autocomplete_fields = ['customer']
    


