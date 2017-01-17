from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^welcome/', include('welcome.urls')),
    url(r'^fastest_segments/', include('fastest_segments.urls')),
    url(r'^most_ridden_segments/', include('most_ridden_segments.urls')),
]

urlpatterns += staticfiles_urlpatterns()
