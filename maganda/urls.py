from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from pages import views
from pictures.conf import app_settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')), 
    path('', include('pages.urls')),
    

]


if app_settings.USE_PLACEHOLDERS:
    urlpatterns += [
        path("_pictures/", include("pictures.urls")),
    ]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)