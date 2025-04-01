from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, ShippingInfo, Order, OrderItem, Promotion
from products.models import Product
from notifications.models import Notification
from .serializers import CartSerializer, OrderSerializer, ShippingInfoSerializer, PromotionSerializer, OrderItemSerializer, CartItemSerializer
from decimal import Decimal

class CartView(generics.RetrieveAPIView):
    """View the current user's cart"""
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        # Check if there are multiple carts for this user
        user_carts = Cart.objects.filter(user=self.request.user)
        
        if user_carts.count() > 1:
            # Multiple carts detected
            main_cart = user_carts.first()  
            
            other_carts = user_carts.exclude(id=main_cart.id)
            
            # Transfer all items from other carts to the main cart
            for other_cart in other_carts:
                for item in other_cart.items.all():
                    # Check if item already exists in main cart
                    try:
                        main_cart_item = main_cart.items.get(product_id=item.product_id)
                        # If it exists, update the quantity
                        main_cart_item.quantity += item.quantity
                        main_cart_item.save()
                    except CartItem.DoesNotExist:
                        # If it doesn't exist, move it to the main cart
                        item.cart = main_cart
                        item.save()
                
                # Delete the other cart after moving all its items
                other_cart.delete()
            
            return main_cart
        
        # Get or create a cart for the user (normal case)
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

class CartAddItemView(APIView):
    """Add a product to the cart"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        if not product_id:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get product
        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check stock
        if product.stock < quantity:
            return Response({'error': f'Only {product.stock} units available'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create cart
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        # Add item to cart
        cart_item = cart.add_item(product, quantity)
        
        # Return updated cart
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CartRemoveItemView(APIView):
    """Remove a product from the cart"""
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, product_id):
        # Get cart
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        # Remove item from cart
        cart.remove_item(product_id)
        
        # Return updated cart
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class CartUpdateItemView(APIView):
    """Update the quantity of a product in the cart"""
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, product_id):
        quantity = int(request.data.get('quantity', 1))
        
        # Get cart
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        # Find the cart item
        try:
            cart_item = cart.items.get(product_id=product_id)
            
            # Check if product has enough stock
            product = Product.objects.get(product_id=product_id)
            if quantity > product.stock:
                return Response({'error': f'Only {product.stock} units available'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Update quantity or remove if zero
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item.delete()
                
            # Return updated cart
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

class CheckoutView(APIView):
    """Process checkout and create an order"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        # Ensure there are items in the cart
        if not cart.items.exists():
            return Response({'error': 'Your cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract shipping info
        shipping_data = {
            'shipping_address': request.data.get('shipping_address', '123 Default St'),
            'city': request.data.get('city', 'Default City'),
            'country': request.data.get('country', 'US'),
            'postal_code': request.data.get('postal_code', '12345'),
        }
        
        # Validate shipping info
        shipping_serializer = ShippingInfoSerializer(data=shipping_data)
        if not shipping_serializer.is_valid():
            return Response(shipping_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Create shipping info
        shipping_info = shipping_serializer.save()
        
        # Create order
        try:
            order = cart.checkout()
            
            # Add shipping info to order
            order.shipping_info = shipping_info
            order.save()
            
            # Process payment
            payment_info = request.data.get('payment_info', {})
            if not payment_info:
                payment_info = {
                    'card_number': '4111111111111111',
                    'expiry_date': '12/2025',
                    'cvv': '123',
                    'name_on_card': 'Test User'
                }
            
            if request.data.get('save_card'):
                from users.models import BillingInfo
                BillingInfo.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'card_number': payment_info.get('card_number'),
                        'expiry_date': payment_info.get('expiry_date'),
                        'cvv': payment_info.get('cvv'),
                        'billing_address': shipping_data['shipping_address']
                    }
                )
            
            order.process_payment(payment_info)
            
            # Create notification for buyer
            Notification.objects.create(
                user=request.user,
                message=f"Your order #{order.order_id} has been placed successfully. Total amount: ${order.total_amount}."
            )
            
            # Create notification for sellers
            for item in order.items.all():
                try:
                    product = Product.objects.get(product_id=item.product_id)
                    seller = product.store.user
                    
                    # Create notification for each unique seller
                    Notification.objects.get_or_create(
                        user=seller,
                        message=f"New order #{order.order_id} received from {request.user.username}. Please check your orders.",
                        defaults={'is_read': False}
                    )
                except Product.DoesNotExist:
                    pass
            
            # Return created order
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            traceback.print_exc()  
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderListView(generics.ListAPIView):
    """List all orders for the authenticated user"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderDetailView(generics.RetrieveAPIView):
    """Get details of a specific order"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_id'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderCancelView(APIView):
    """Cancel an order and initiate a refund"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id, user=request.user)
        
        if order.payment_status == 'PAID' and order.order_status != 'DELIVERED' and order.order_status != 'CANCELLED':
            # Refund payment
            order.payment.refund_payment()
            
            # Create notification for the order cancellation
            Notification.objects.create(
                user=request.user,
                message=f"Your order #{order.order_id} has been cancelled and payment refunded."
            )
            
            # Notify sellers about the cancellation
            for item in order.items.all():
                try:
                    product = Product.objects.get(product_id=item.product_id)
                    seller = product.store.user
                    Notification.objects.create(
                        user=seller,
                        message=f"Order #{order.order_id} from {order.user.username} has been cancelled."
                    )
                    
                    # Restore stock
                    product.stock += item.quantity
                    product.save()
                except Product.DoesNotExist:
                    pass
                    
            # Return updated order
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        else:
            return Response({'error': 'This order cannot be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

class ApplyPromotionView(APIView):
    """Apply a promotion code to the current cart"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        discount_code = request.data.get('discount_code')
        if not discount_code:
            return Response({'error': 'Discount code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            promotion = Promotion.objects.get(discount_code=discount_code)
        except Promotion.DoesNotExist:
            return Response({'error': 'Invalid discount code'}, status=status.HTTP_404_NOT_FOUND)
        
        # Return promotion details
        serializer = PromotionSerializer(promotion)
        return Response(serializer.data)

class SellerOrderListView(generics.ListAPIView):
    """List all orders that contain products from the seller's store"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            if self.request.user.role != 'SELLER' or not hasattr(self.request.user, 'store'):
                return Order.objects.none()
                
            store = self.request.user.store
            
            store_product_ids = list(store.products.values_list('product_id', flat=True))
            
            store_order_items = OrderItem.objects.filter(product_id__in=store_product_ids)
            
            order_ids = store_order_items.values_list('order', flat=True).distinct()
            
            orders = Order.objects.filter(id__in=order_ids).order_by('-created_at')
            
            status_filter = self.request.query_params.get('status')
            if status_filter and status_filter != 'ALL':
                orders = orders.filter(order_status=status_filter)
                
            return orders
            
        except Exception as e:
            import traceback
            print(f"Error in SellerOrderListView.get_queryset: {str(e)}")
            print(traceback.format_exc())
            return Order.objects.none() 

class SellerOrderDetailView(generics.RetrieveAPIView):
    """Get details of a specific order for a seller - only if it contains their products"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_id'
    
    def get_queryset(self):
        try:
            # Check if user is a seller and has a store
            if self.request.user.role != 'SELLER' or not hasattr(self.request.user, 'store'):
                return Order.objects.none()
                
            store = self.request.user.store
            
            # Get all product IDs from this store
            store_product_ids = list(store.products.values_list('product_id', flat=True))
            
            # Get orders that contain the seller's products
            from django.db.models import Exists, OuterRef
            
            # Find order items that contain this seller's products
            order_item_subquery = OrderItem.objects.filter(
                order=OuterRef('pk'),
                product_id__in=store_product_ids
            )
            
            # Return orders that contain these items
            return Order.objects.filter(
                Exists(order_item_subquery)
            )
                
        except Exception as e:
            import traceback
            print(f"Error in SellerOrderDetailView.get_queryset: {str(e)}")
            print(traceback.format_exc())
            return Order.objects.none()

class SellerOrderUpdateStatusView(APIView):
    """Update order status for seller - only if it contains their products"""
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, order_id):
        try:
            # Check if user is a seller and has a store
            if request.user.role != 'SELLER' or not hasattr(request.user, 'store'):
                return Response({'error': 'Only sellers can update order status'}, status=status.HTTP_403_FORBIDDEN)
                
            store = request.user.store
            
            # Get all product IDs from this store
            store_product_ids = list(store.products.values_list('product_id', flat=True))
            
            # Find the order
            order = get_object_or_404(Order, order_id=order_id)
            
            # Check if order contains products from this seller
            order_contains_seller_products = OrderItem.objects.filter(
                order=order, 
                product_id__in=store_product_ids
            ).exists()
            
            if not order_contains_seller_products:
                return Response({'error': 'You do not have permission to update this order'}, 
                                status=status.HTTP_403_FORBIDDEN)
            
            # Get new status and validate
            new_status = request.data.get('status')
            valid_statuses = [status_option for status_option, _ in Order.ORDER_STATUS]
            
            if not new_status or new_status not in valid_statuses:
                return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
                
            # Update order status
            order.order_status = new_status
            order.save()
            
            # Create notification for buyer
            Notification.objects.create(
                user=order.user,
                message=f"Your order #{order.order_id} status has been updated to {new_status}."
            )
            
            # Return updated order
            serializer = OrderSerializer(order)
            return Response(serializer.data)
            
        except Exception as e:
            import traceback
            print(f"Error in SellerOrderUpdateStatusView: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MergeCartView(APIView):
    """Merge guest cart with user cart after login"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            guest_cart_items = request.data.get('items', [])
            if not guest_cart_items:
                return Response({'message': 'No items to merge'}, status=status.HTTP_200_OK)
            
            cart, _ = Cart.objects.get_or_create(user=request.user)
            
            for item in guest_cart_items:
                try:
                    product = Product.objects.get(product_id=item['product_id'])
                    quantity = int(item['quantity'])
                    
                    # Check if item already exists in cart
                    try:
                        cart_item = cart.items.get(product_id=product.product_id)
                        cart_item.quantity += quantity
                        cart_item.save()
                    except CartItem.DoesNotExist:
                        CartItem.objects.create(
                            cart=cart,
                            product_id=product.product_id,
                            quantity=quantity,
                            price=product.price
                        )
                except Product.DoesNotExist:
                    continue
            
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to merge cart: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
