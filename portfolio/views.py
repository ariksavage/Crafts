from django.shortcuts import render

from .models import Visit


def home(request):
    name = request.GET.get("name", "stranger")
    Visit.objects.create(path=request.path)
    visits = Visit.objects.filter(path=request.path).count()
    return render(request, "portfolio/home.html", {"name": name, "visits": visits})


def about(request):
    crafts = ["Furniture", "Art", "Fabric Crafts"]
    Visit.objects.create(path=request.path)
    return render(request, "portfolio/about.html", {"crafts": crafts})
