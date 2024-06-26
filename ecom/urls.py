"""
URL configuration for ecom project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import debug_toolbar
from django.conf import Settings
from django.conf.urls.static import static

from ecom import settings


admin.site.site_header = 'Ecommerce Backend'
admin.site.index_title = 'Django DRF'

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('playground/', include('playground.urls')), 
    path("__debug__/", include("debug_toolbar.urls")),
    path('store/', include('store.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    
]
if settings.DEBUG : 
    urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)