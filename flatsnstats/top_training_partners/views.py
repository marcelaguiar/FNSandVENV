from django.shortcuts import render


def index(request):
    return render(request, 'top_training_partners/index.html')
