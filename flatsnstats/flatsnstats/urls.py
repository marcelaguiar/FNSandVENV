from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^welcome/', views.welcome, name='welcome'),
    url(r'^top_training_partners/', views.top_training_partners, name='top_training_partners'),
    url(r'^fastest_segments/', views.fastest_segments, name='fastest_segments'),
    url(r'^most_ridden_segments/', views.most_ridden_segments, name='most_ridden_segments'),
    url(r'^admin/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()
