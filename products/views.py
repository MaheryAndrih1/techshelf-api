from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Like
from django.db.models import Q

def product_list_view(request):
    products = Product.objects.all()
    
    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)
    
    # Filter by search term if provided
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) |
            Q(category__icontains=search)
        )
    
    # Filter by price range if provided
    min_price = request.GET.get('min_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    
    max_price = request.GET.get('max_price')
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sort products
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    elif sort == 'popularity':
        products = products.order_by('-like__count')
    else:  # Default to newest
        products = products.order_by('-created_at')
    
    # Get unique categories for the filter sidebar
    categories = Product.objects.values_list('category', flat=True).distinct()
    
    context = {
        'products': products,
        'categories': categories,
    }
    
    return render(request, 'products/list.html', context)

def product_detail_view(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    context = {
        'product': product,
    }
    return render(request, 'products/detail.html', context)

def product_category_view(request, category):
    products = Product.objects.filter(category=category)
    categories = Product.objects.values_list('category', flat=True).distinct()
    context = {
        'products': products,
        'categories': categories,
        'current_category': category,
    }
    return render(request, 'products/list.html', context)

@login_required
def create_product_view(request):
    if request.user.role != 'SELLER':
        messages.error(request, 'You need to be a seller to create products.')
        return redirect('users:upgrade_seller')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category = request.POST.get('category')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        product = Product(
            name=name,
            price=price,
            stock=stock,
            category=category,
            description=description,
            image=image,
            store=request.user.store
        )
        product.save()
        
        messages.success(request, f'Product "{name}" has been created.')
        return redirect('products:detail', product_id=product.product_id)
    
    return render(request, 'products/create.html')

@login_required
def edit_product_view(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    
    # Check if the user owns this product
    if request.user != product.store.user:
        messages.error(request, 'You do not have permission to edit this product.')
        return redirect('products:detail', product_id=product_id)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.category = request.POST.get('category')
        product.description = request.POST.get('description')
        
        if 'image' in request.FILES:
            product.image = request.FILES.get('image')
        
        product.save()
        messages.success(request, f'Product "{product.name}" has been updated.')
        return redirect('products:detail', product_id=product.product_id)
    
    context = {
        'product': product,
    }
    return render(request, 'products/edit.html', context)

@login_required
def like_product_view(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, product_id=product_id)
        
        # Check if the user has already liked this product
        try:
            like = Like.objects.get(user=request.user, product=product)
            # User has already liked this product, so unlike it
            like.delete()
        except Like.DoesNotExist:
            # Create a new like with proper like_id
            like = Like(
                user=request.user,
                product=product,
                like_id=f"like_{request.user.id}_{product.product_id}"
            )
            like.save()
        
        return redirect('products:detail', product_id=product_id)
