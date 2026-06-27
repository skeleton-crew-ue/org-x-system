from django.shortcuts import render

# Esta es la vista que falta
def home(request):
    return render(request, 'home.html')

# Estas son las vistas para tus páginas de error personalizadas
def custom_page_not_found(request, exception):
    return render(request, '404.html', status=404)

def custom_error_view(request):
    return render(request, '500.html', status=500)
    