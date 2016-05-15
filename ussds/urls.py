from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.views import static
admin.autodiscover()



# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^',include('ussdke.urls')),
    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', static.serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^static/(?P<path>.*)$', static.serve, {
            'document_root': settings.STATIC_ROOT,
        }),
        ]
