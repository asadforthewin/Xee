
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from store.admin import ProductAdmin, ProductImageInline
from core.models import TaggedItem
from store.models import Product
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "email", "first_name", "last_name"),
            },
        ),
    )

class TagIteminline(GenericTabularInline):
    model = TaggedItem
    autocomplete_fields = ['tag']


class CustomProductAdmin(ProductAdmin):
    inlines = [TagIteminline, ProductImageInline]
    
admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)