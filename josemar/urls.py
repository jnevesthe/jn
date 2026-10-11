from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

from portifolio.urls import i18n_urlpatterns


# ===== Rotas SEM prefixo (admin + sitemap, robots, ads.txt, i18n do portifolio) =====
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("portifolio.urls")),
]


# ===== Rotas COM prefixo de idioma (PT sem prefixo, /en/..., /es/...) =====
urlpatterns += i18n_patterns(
    path("", include(i18n_urlpatterns)),
    prefix_default_language=False,
)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
