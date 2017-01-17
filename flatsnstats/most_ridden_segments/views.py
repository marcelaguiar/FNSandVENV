from django.shortcuts import render


def index(request):
    return render(request, 'most_ridden_segments/index.html')
