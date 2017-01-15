from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^welcome/', include('welcome.urls')),
    # url(r'^$', include('welcome.urls')), #if user isnt connected and they go to homepage, redirect to welcome page
]

urlpatterns += staticfiles_urlpatterns()
