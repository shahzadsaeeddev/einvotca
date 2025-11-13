from django_filters import rest_framework as filters

from .models import ZatcaInvoicesProduction

class InvoiceFilter(filters.FilterSet):

    start_date = filters.DateFilter(field_name='created_at',
                                             lookup_expr='gte')
    end_date = filters.DateFilter(field_name='created_at',
                                           lookup_expr='lte')
    createdBy__slug = filters.CharFilter(field_name='createdBy__slug')  # Assuming createdBy is a CharField
    invoice_scope = filters.CharFilter(field_name='invoiceScope')  # Replace with the correct field name
    invoice_type = filters.CharFilter(field_name='invoiceType')  # Replace with the correct field name
    compliance = filters.BooleanFilter(field_name='compliance')  # Assuming compliance is a BooleanField

    class Meta:
        model = ZatcaInvoicesProduction
        fields = ['start_date','end_date', 'createdBy__slug', 'invoice_scope', 'invoice_type', 'compliance']
