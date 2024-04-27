from cgitb import lookup
from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('products', views.ProductViewset, basename='products')
router.register('collection', views.CollectionViewset)
router.register('cart', views.CartViewset)
router.register('customers', views.CustomerViewset)
router.register('orders', views.OrderViewset, basename='orders')

products_router = routers.NestedDefaultRouter(router, 'products', lookup = 'product')
products_router.register('reviews', views.ReviewViewset, basename='product-reviews')

products_router.register('images', views.ProductImageViewset, basename='product-images')

cart_router = routers.NestedDefaultRouter(router, 'cart', lookup = 'cart')
cart_router.register('items', views.CartItemViewset, basename='cart-items')

urlpatterns = router.urls + products_router.urls +cart_router.urls 
 
