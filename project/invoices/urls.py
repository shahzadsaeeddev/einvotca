from django.urls import path

from .views import ProductionInvoiceView, ProductionInvoiceDashboardView

app_name='invoices'
urlpatterns = [
   # path('business-types/', BusinessTypesView.as_view(), name="business-types"),

path('invoices/', ProductionInvoiceView.as_view(),
         name='production/invoices/'),
path('invoices/dashboard/', ProductionInvoiceDashboardView.as_view(),
         name='invoices/dashboard/'),
]

