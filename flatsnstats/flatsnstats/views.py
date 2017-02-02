from django.shortcuts import render
from . import userdata


first_name = userdata.first_name
last_name = userdata.last_name


def index(request):
    return render(request, 'index.html', {
        'first_name': first_name,
        'last_name': last_name
    })


def handler404(request):
    return render(request, '404.html')


def handler500(request):
    return render(request, '500.html')
