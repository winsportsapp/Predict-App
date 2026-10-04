"""
URL configuration for config project.
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from predictions.views import (
    ads_txt,
    media_file,
    offline,
    robots_txt,
    service_worker,
    sitemap_xml,
    web_manifest,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Installable app (PWA). The service worker must be served from the root
    # so its scope covers the whole site.
    path("manifest.webmanifest", web_manifest, name="web_manifest"),
    path("sw.js", service_worker, name="service_worker"),
    path("offline/", offline, name="offline"),
    # Crawler and ad-network files, served from the site root.
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap_xml, name="sitemap_xml"),
    path("ads.txt", ads_txt, name="ads_txt"),
    # Login uses Django's LoginView. Template: templates/registration/login.html
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(redirect_authenticated_user=True),
        name="login",
    ),
    # Built-in logout (POST only) plus password-reset URLs.
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("predictions.urls")),
]

# Uploaded media (e.g. team flags) is stored in the database and served from
# there in every environment; see predictions.storage.DatabaseStorage.
urlpatterns += [
    path(f"{settings.MEDIA_URL.strip('/')}/<path:path>", media_file, name="media"),
]
