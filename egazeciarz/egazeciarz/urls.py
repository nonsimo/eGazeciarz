from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(
        r'^$',
        TemplateView.as_view(template_name="egazeciarz/index.html"),
        name="home",
    ),
    url(r'^profile/',
        TemplateView.as_view(template_name="account/account_panel.html"), name="profile",),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^services/', include('services.urls', namespace='services')),
)

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_ROOT,
        document_root=settings.STATIC_ROOT)
