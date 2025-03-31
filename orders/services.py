from .models import Order, OrderItem
from products.models import Product

class OrderService:
    @staticmethod
    def create_order_from_cart(cart):
        if not cart.user:
            raise ValueError("Cannot create order for guest cart")
        
        # Calculate totals
        total_amount = 0
        items = []
        
        for cart_item in cart.items.all():
            try:
                product = Product.objects.get(product_id=cart_item.product_id)
                if product.stock < cart_item.quantity:
                    raise ValueError(f"Not enough stock for product: {product.name}")
                
                item_total = product.price * cart_item.quantity
                total_amount += item_total
                
                items.append({
                    'product': product,
                    'quantity': cart_item.quantity,
                    'price': product.price
                })
            except Product.DoesNotExist:
                raise ValueError(f"Product with ID {cart_item.product_id} does not exist")
        
        # Create order
        order = Order.objects.create(
            user=cart.user,
            total_amount=total_amount,
            tax_rate=0.0,  # Set appropriate tax rate in production
            shipping_cost=0.0  # Calculate shipping cost in production
        )
        
        # Create order items
        for item in items:
            OrderItem.objects.create(
                order=order,
                product_id=item['product'].product_id,
                quantity=item['quantity'],
                price=item['price']
            )
            
            # Decrement stock
            item['product'].decrement_stock(item['quantity'])
        
        # Clear cart
        cart.items.all().delete()
        
        return order
