from django.shortcuts import render
from .models import Product

def home(request):
    queryset = Product.objects.filter(category__title__icontains='the')
    return render(request, 'home.html', {'products': list(queryset)})
