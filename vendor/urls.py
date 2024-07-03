"""sprint_mis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from api import views
from vendor import settings

urlpatterns = [
    path('admin/', admin.site.urls),

############### Vendor ############################

    path('vendors/', views.create_vendor, name='create_vendor'),
    path('api/get_vendor/<int:vendor_id>/', views.get_vendor, name='get_vendor'),
    path('api/update_vendor/<int:vendor_id>/', views.update_vendor, name='update_vendor'),
    path('api/delete_vendor/<int:vendor_id>/', views.delete_vendor, name='delete_vendor'),
    path('api/get_vendor_performance/<int:vendor_id>/', views.get_vendor_performance, name='get_vendor_performance'),

################ Purchase Order ####################

    path('api/purchase_orders/', views.create_po, name='create_po'),
    path('api/purchase_orders/<int:po_id>/', views.get_po, name='get_po'),
    path('api/update_po/<int:po_id>/', views.update_po, name='update_po'),
    path('api/delete_po/<int:po_id>/', views.delete_po, name='delete_po'),

    path('register/', views.register, name='register'),


]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
