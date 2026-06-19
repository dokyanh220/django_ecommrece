from django.shortcuts import render
from app.models import Category, Product

def home(request):
    products = Product.objects.filter(status=True).select_related('category').order_by('-created_at')[:8]
    categories = Category.objects.all()[:8]

    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
    })
