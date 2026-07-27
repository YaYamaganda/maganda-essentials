from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Product, Category
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, ProductReview



class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True)
        
        # Filter by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        
        # Filter by soap type
        soap_type = self.request.GET.get('type')
        if soap_type:
            queryset = queryset.filter(soap_type=soap_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['current_category'] = self.kwargs.get('category_slug')
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            is_available=True
        ).exclude(id=self.object.id)[:4]
        return context


def add_review(request, product_id):
    """Add a product review"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        comment = request.POST.get('comment')
        
        if all([name, email, rating, title, comment]):
            review = ProductReview.objects.create(
                product=product,
                name=name,
                email=email,
                rating=int(rating),
                title=title,
                comment=comment,
                is_approved=False  # Requires admin approval
            )
            messages.success(request, 'Thank you for your review! It will be published after approval.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return redirect('products:product_detail', slug=product.slug)
