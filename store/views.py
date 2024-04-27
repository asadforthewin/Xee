from django.shortcuts import get_object_or_404
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from .permissions import ViewCustomerHistory
from store.permissions import IsAdminOrReadOnly, ViewCustomerHistory
from .serializers import AddCartItemSerializer, CartItemSerializer, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductImageSerializer, ProductSerializer, CollectionSerializer, ReviewSerializer, CartSerializer, UpdateCartItemSerializer, UpdateOrderSerializer
from .models import Cart, Customer, Order, Product, Collection, OrderItem, ProductImage, Review, CartItem
from .filters import ProductFilter
from .pagination import DefaultPagination
from store import permissions

class ProductViewset(ModelViewSet):
    
    queryset = Product.objects.prefetch_related('images').all()
    permission_classes = [IsAdminOrReadOnly]    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']
    
   
    '''
        Due to filterbackends of generic filtering, we can completely remove thsi logic and get back to 
        queryset = products.objects.all()
   
    def get_queryset(self):
        queryset = Product.objects.all()
        collection_id = collection_id = self.request.query_params.get('collection_id')
        if collection_id is not None:
            queryset = queryset.filter(collection_id = collection_id)
        return queryset
   ''' 
    
    serializer_class = ProductSerializer
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
                return Response({'error':'Cant be deleted as associated with orderitem'} ,status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
    
    # def delete(self,request, pk):
    #     product = get_object_or_404(Product, pk=pk)
    #     if product.orderitems.count() > 0:
    #             return Response({'error':'Cant be deleted as associated with orderitem'} ,status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #     product.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    
'''
(3)
class ProductList(ListCreateAPIView):
    queryset = Product.objects.select_related('collection').all()
    serializer_class = ProductSerializer
    
    # def get_queryset(self): if queryset is simple no need to override these methods
    #     return Product.objects.select_related('collection').all()
    
    # def get_serializer_class(self):
    #     return ProductSerializer
    
    def get_serializer_context(self):
        return {'request': self.request}
(2)
class ProductList(APIView):
    
    def get(self, request):
        queryset= Product.objects.select_related('collection').all()
        serializer = ProductSerializer(queryset , many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        
        serializer = ProductSerializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        
    
(1)
@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        queryset= Product.objects.select_related('collection').all()
        serializer = ProductSerializer(queryset , many=True, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
 
class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
        
    def delete(self,request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count() > 0:
                return Response({'error':'Cant be deleted as associated with orderitem'} ,status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductDetail(APIView):
    
    def get(self,request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    
    def put(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status= status.HTTP_200_OK )
        
    def delete(self, id):
        product = get_object_or_404(Product, pk=id)
        if product.orderitems.count() > 0:
                return Response({'error':'Cant be deleted as associated with orderitem'} ,status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        

        
        

@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, id):
        product = get_object_or_404(Product, pk=id)
        if request.method == 'GET':
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        elif request.method =='PUT':
            serializer = ProductSerializer(product, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status= status.HTTP_200_OK )
        elif request.method == 'DELETE':
            if product.orderitems.count() > 0:
                return Response({'error':'Cant be deleted as associated with orderitem'} ,status=status.HTTP_405_METHOD_NOT_ALLOWED)
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
'''
   
class CollectionViewset(ModelViewSet):
    queryset = Collection.objects.annotate(products_count= Count('products')). all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def delete(self, request, pk):
        collection = get_object_or_404(Collection.objects.annotate(products_count= Count('products')).all() , pk=pk)
        if collection.products.count()>0:
            return Response({'error':'cant be deleted due to products'}, status= status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 
    
    
'''
class CollectionList(ListCreateAPIView):
    def get_queryset(self):
        return Collection.objects.annotate(products_count= Count('products')). all()
    
    serializer_class = CollectionSerializer
 
            
@api_view(['GET', 'POST'])
def collection_list(request):
    if request.method == 'GET':
        queryset = Collection.objects.annotate(products_count= Count('products')). all()
        serializer = CollectionSerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CollectionSerializer( data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status =status.HTTP_201_CREATED )

class CollectionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(products_count= Count('products')).all()
    serializer_class = CollectionSerializer
    
    def delete(self, request, pk):
        collection = get_object_or_404(Collection.objects.annotate(products_count= Count('products')).all() , pk=pk)
        if collection.products.count()>0:
            return Response({'error':'cant be deleted due to products'}, status= status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 
    

@api_view(['GET', 'PUT', 'DELETE'])
def collection_detail(request,pk):
    collection = get_object_or_404(Collection.objects.annotate(products_count= Count('products')).all() , pk=pk)
    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        if collection.products.count()>0:
            return Response({'error':'cant be deleted due to products'}, status= status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 
'''

class ReviewViewset(ModelViewSet):
    
    def get_queryset(self):
       return Review.objects.filter(product_id=self.kwargs['product_pk'])

    serializer_class = ReviewSerializer
    
    def get_serializer_context(self):
         return {'product_id': self.kwargs['product_pk']}
    
    
class CartViewset(CreateModelMixin, RetrieveModelMixin,DestroyModelMixin, GenericViewSet):
    
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
    
class CartItemViewset(ModelViewSet):
    
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def get_queryset(self):
        return CartItem.objects.filter(cart_id = self.kwargs['cart_pk']).select_related('product')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}
    
class CustomerViewset(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]
    
    @action(detail=True, permission_classes= [ViewCustomerHistory])
    def history(self, request,pk):
        return Response('ok')
    
    @action(detail=False, methods=['GET', 'PUT'], permission_classes= [IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id = request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        
class OrderViewset(ModelViewSet):
    
    http_method_names = ['get','patch','post',  'delete', 'head', 'options']
    
    def get_permissions(self):
        if self.request.method == ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context ={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        
        customer_id = Customer.objects.only('id'). get(user_id = self.request.user.id)
        return Order.objects.filter(customer_id=customer_id)
    
class ProductImageViewset(ModelViewSet):
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')
    
    def get_queryset(self):
        return ProductImage.objects.select_related('product').filter(product_id = self.kwargs['product_pk'])
    
        
    def get_permissions(self):
        if self.request.method  == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]
        
    serializer_class = ProductImageSerializer
    
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
            