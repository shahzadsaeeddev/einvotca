"""
URL configuration for neksio_pos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.http.response import HttpResponse
from django.urls import path, re_path, include
from django.conf import settings

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls.static import static

schema_view = get_schema_view(
   openapi.Info(
      title="Neksio API",
      default_version='V0.1',
      description="Neksio API description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="bilaljmal@gmail.com"),
      license=openapi.License(name="Neksio License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)
def trigger_error(request):
    division_by_zero = 1 / 0

def index(request):
    return HttpResponse("Oops, Invalid url parameters")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('accounts/', include("accounts.urls"), name="account"),
    path('api/', include("neksio_api.urls"), name="api"),
    path('zatca/', include("zatca_api.urls"), name="zatca"),
    path('invoices/', include("invoices.urls"), name="invoices"),
    path('products/', include("products.urls"), name="products"),
    path('transactions/', include("transactions.urls"), name="transactions"),
    path('sentry-debug/', trigger_error),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


swagger_url = [
   re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


if settings.DEBUG:
    urlpatterns += swagger_url