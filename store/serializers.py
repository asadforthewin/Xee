from django.db import transaction
from rest_framework import serializers
from decimal import Decimal
from store.signals import order_created
from . import models

# class CollectionSerializer(serializers.Serializer):
    
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length= 255)
    
class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ['id', 'title', 'products_count']
        
    products_count = serializers.IntegerField(read_only=True)
    
            
        
    
    
    
# class ProductSerializer(serializers.Serializer):
    
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     price = serializers.DecimalField(decimal_places=2, max_digits=4, source = 'unit_price')
#     

class ProductImageSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        product_id = self.context['product_id']
        return models.ProductImage.objects.create(product_id = product_id, **validated_data)
    
    
    class Meta:
        model = models.ProductImage
        fields = ['id', 'image']
        
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many = True, read_only =True)
    class Meta:
        model = models.Product
        fields = ['id', 'title','slug', 'inventory','description', 'unit_price', 'price_with_tax', 'collection','images']
        
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    collection = serializers.PrimaryKeyRelatedField(
        queryset = models.Collection.objects.all()
    )
    
    def calculate_tax(self, product):
        return product.unit_price * Decimal(1.1)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model= models.Review
        fields = ['id','name', 'date', 'description']
        
    
    def create(self, validated_data):
        product_id = self.context['product_id']
        return models.Review.objects.create(product_id = product_id, **validated_data)
    
    
    
class SimpleProductserializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['id', 'title', 'unit_price']
        
class CartItemSerializer(serializers.ModelSerializer):
    
    product = SimpleProductserializer()
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(self, cart_item: models.CartItem):
        return cart_item.quantity * cart_item.product.unit_price
        
    class Meta:
        model = models.CartItem
        fields = ['id', 'product', 'quantity', 'total_price']
        
    
        
class CartSerializer(serializers.ModelSerializer):
    
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True )
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(Self, cart:models.Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all() ])
        
    class Meta:
        model = models.Cart
        fields = ['id', 'items', 'total_price']
 
 
class AddCartItemSerializer(serializers.ModelSerializer):
    
    product_id = serializers.IntegerField()
    
    class Meta:
        model = models.CartItem
        fields = ['id', 'product_id', 'quantity']
        
    def validate_product_id(self, value):
        if not models.Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with given ID exists')
        return value
        
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:
            cart_item= models.CartItem.objects.get(cart_id = cart_id, product_id= product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except models.CartItem.DoesNotExist:
            self.instance = models.CartItem.objects.create(cart_id = cart_id, **self.validated_data)
        return self.instance
    
class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = [ 'quantity']
        
class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only= True)
    class Meta:
        model = models.Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']
        
class OrderItemSerializer(serializers.ModelSerializer):
    
    product = SimpleProductserializer()
    class Meta:
        model = models.OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity']
        
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only= True)
    
    class Meta:
        model = models.Order
        fields = ['id', 'placed_at', 'customer', 'payment_status', 'items']
        
class CreateOrderSerializer(serializers.Serializer):
    
    cart_id = serializers.UUIDField()
    
    def validate_cart_id(self, cart_id):
        if not models.Cart.objects.filter(pk = cart_id).exists():
            raise serializers.ValidationError('No cart with the given id is found')
        elif models.CartItem.objects.filter(cart_id= cart_id). count() ==0:
            raise serializers.ValidationError('The cart is empty')
        return cart_id
    
    def save(self, **kwargs):
        
        # print(self.validated_data['cart_id'])
        # print([self.context['user_id']])
        with transaction.atomic():
            customer = models.Customer.objects.get(user_id = self.context['user_id'])
            order = models.Order.objects.create(customer=customer )
            
            cart_items = models.CartItem.objects.select_related('product').filter(cart_id = self.validated_data['cart_id'])
            order_items = [models.OrderItem(
                    order = order,
                    product = item.product,
                    unit_price = item.product.unit_price,
                    quantity= item.quantity 
                                                
                                ) for item in cart_items]
            
            models.OrderItem.objects.bulk_create(order_items)
            
            models.Cart.objects.filter(pk= self.validated_data['cart_id']). delete()
            
            order_created.send_robust(self.__class__, order = order)
            return order
        
        
class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta: 
        model = models.Order
        fields = ['payment_status']
                
        

        
        
    
    
    
    