from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Store, StoreTheme, Rating
from .forms import StoreCreationForm, StoreEditForm, StoreThemeForm, RatingForm

def landing_page_view(request):
    featured_stores = Store.objects.all()[:6]
    return render(request, 'landing/home.html', {'featured_stores': featured_stores})

def about_view(request):
    return render(request, 'landing/about.html')

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Here you would typically handle the form submission, e.g., send an email
        # For demonstration, we'll just display a success message
        messages.success(request, 'Thank you for contacting us. We will get back to you shortly.')
        return redirect('landing:contact')
    
    return render(request, 'landing/contact.html')

def how_it_works_view(request):
    return render(request, 'landing/how_it_works.html')

def store_list_view(request):
    stores = Store.objects.all()
    return render(request, 'stores/list.html', {'stores': stores})

@login_required
def create_store_view(request):
    if request.user.role != 'SELLER':
        messages.error(request, 'You need to be a seller to create a store.')
        return redirect('users:upgrade_seller')
    
    if request.method == 'POST':
        form = StoreCreationForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.user = request.user
            
            # Create theme
            theme = StoreTheme.objects.create(
                primary_color=request.POST.get('primary_color', '#3498db'),
                secondary_color=request.POST.get('secondary_color', '#2ecc71'),
                font=request.POST.get('font', 'Roboto')
            )
            
            if 'logo_url' in request.FILES:
                theme.logo_url = request.FILES['logo_url']
            if 'banner_url' in request.FILES:
                theme.banner_url = request.FILES['banner_url']
            
            theme.save()
            store.theme = theme
            store.save()
            
            messages.success(request, 'Store created successfully.')
            return redirect('stores:detail', subdomain=store.subdomain_name)
        else:
            messages.error(request, 'There was an error creating the store. Please check the form for errors.')
    else:
        form = StoreCreationForm()
        
    return render(request, 'stores/create.html', {'form': form})

def store_detail_view(request, subdomain):
    store = get_object_or_404(Store, subdomain_name=subdomain)
    products = store.products.all()
    return render(request, 'stores/detail.html', {'store': store, 'products': products})

@login_required
def edit_store_view(request, subdomain):
    store = get_object_or_404(Store, subdomain_name=subdomain)
    
    if request.user != store.user:
        messages.error(request, 'You do not have permission to edit this store.')
        return redirect('stores:detail', subdomain=subdomain)
    
    if request.method == 'POST':
        form = StoreEditForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, 'Store updated successfully.')
            return redirect('stores:detail', subdomain=form.instance.subdomain_name)
        else:
            messages.error(request, 'There was an error updating the store. Please check the form for errors.')
    else:
        form = StoreEditForm(instance=store)
        
    return render(request, 'stores/edit.html', {'store': store, 'form': form})

@login_required
def store_theme_view(request, subdomain):
    store = get_object_or_404(Store, subdomain_name=subdomain)
    
    if request.user != store.user:
        messages.error(request, 'You do not have permission to edit this store theme.')
        return redirect('stores:detail', subdomain=subdomain)
    
    # Get or create theme with a proper ID
    theme, created = StoreTheme.objects.get_or_create(
        defaults={
            'primary_color': '#3498db',
            'secondary_color': '#2ecc71',
            'font': 'Roboto'
        }
    )
    
    if created:
        # Set theme_id properly after creation
        theme.theme_id = f"theme_{store.store_id}"
        theme.save()
        
        # Associate theme with store if it's new
        store.theme = theme
        store.save()
    
    if request.method == 'POST':
        form = StoreThemeForm(request.POST, request.FILES, instance=theme)
        if form.is_valid():
            form.save()
            messages.success(request, 'Store theme updated successfully.')
            return redirect('stores:detail', subdomain=subdomain)
        else:
            messages.error(request, 'There was an error updating the theme. Please check the form for errors.')
    else:
        form = StoreThemeForm(instance=theme)
        
    return render(request, 'stores/theme.html', {'store': store, 'form': form})

def store_ratings_view(request, subdomain):
    store = get_object_or_404(Store, subdomain_name=subdomain)
    ratings = store.ratings.all().order_by('-timestamp')
    return render(request, 'stores/ratings.html', {'store': store, 'ratings': ratings})

@login_required
def rate_store_view(request, subdomain):
    store = get_object_or_404(Store, subdomain_name=subdomain)
    
    # Check if user is the store owner
    if request.user == store.user:
        messages.error(request, 'You cannot rate your own store.')
        return redirect('stores:detail', subdomain=subdomain)
    
    # Check if user already rated this store
    existing_rating = Rating.objects.filter(user=request.user, store=store).first()
    
    if request.method == 'POST':
        if existing_rating:
            form = RatingForm(request.POST, instance=existing_rating)
        else:
            form = RatingForm(request.POST)
            
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.store = store
            rating.rating_id = f"rating_{request.user.id}_{store.store_id}"
            rating.save()
            messages.success(request, 'Rating submitted successfully.')
            return redirect('stores:ratings', subdomain=subdomain)
        else:
            messages.error(request, 'There was an error submitting your rating. Please check the form for errors.')
    else:
        form = RatingForm(instance=existing_rating) if existing_rating else RatingForm()
    
    return render(request, 'stores/rate.html', {'store': store, 'form': form})

