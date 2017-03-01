from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^welcome/', include('welcome.urls')),
    url(r'top_training_partners', include('top_training_partners.urls')),
    url(r'^fastest_segments/', include('fastest_segments.urls')),
    url(r'^most_ridden_segments/', include('most_ridden_segments.urls')),
]

urlpatterns += staticfiles_urlpatterns()
