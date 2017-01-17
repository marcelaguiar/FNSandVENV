from django.shortcuts import render


def index(request):
    return render(request, 'fastest_segments/index.html')
