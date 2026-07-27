from django.shortcuts import redirect, render
from django.contrib import messages

from products.models import Product


def home(request):
    # Get featured products (is_featured=True) or fallback to newest
    featured_products = Product.objects.filter(is_available=True, is_featured=True)[:6]
    
    # If no featured products, show the 6 newest
    if not featured_products:
        featured_products = Product.objects.filter(is_available=True).order_by('-created_at')[:6]
    
    return render(request, 'home.html', {
        'featured_products': featured_products
    })

def about(request):
    return render(request, 'about.html')


def newsletter_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # TODO: Save email to database or send to Mailchimp
            messages.success(request, 'Thank you for subscribing! 🌿')
        else:
            messages.error(request, 'Please enter a valid email address.')
    return redirect('pages:home')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # TODO: Send email or save to database
        # For now, just show a success message
        messages.success(request, 'Thank you for your message! We\'ll get back to you soon. 🌿')
        return redirect('pages:about')
    
    return redirect('pages:about')


def thank_you(request):
    return render(request, 'pages/thank_you.html')