from django_filters import rest_framework as filters

from .models import JournalDetail, JournalLine


class JournalDetailFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    end_date = filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model = JournalDetail
        fields = ['start_date', 'end_date', 'transaction__transaction_type', 'account']



class SaleReportFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='date_time', lookup_expr='date__gte')
    end_date = filters.DateFilter(field_name='date_time', lookup_expr='date__lte')
    category = filters.CharFilter(field_name='items_transactions__item__category__id')

    class Meta:
        model = JournalLine
        fields = ['start_date', 'end_date', 'transaction_type', 'party__id', 'category']


class InventoryReportFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='date_time', lookup_expr='date__gte')
    end_date = filters.DateFilter(field_name='date_time', lookup_expr='date__lte')
    product_id = filters.CharFilter(field_name='items_transactions__item__id')

    class Meta:
        model = JournalLine
        fields = ['start_date', 'end_date', 'party__id', 'product_id']



class SaleInvoiceFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='date_time', lookup_expr='date__gte')
    end_date = filters.DateFilter(field_name='date_time', lookup_expr='date__lte')

    class Meta:
        model = JournalLine
        fields = ['start_date', 'end_date', 'party__id']


class PurchaseFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='date_time', lookup_expr='date__gte')
    end_date = filters.DateFilter(field_name='date_time', lookup_expr='date__lte')

    class Meta:
        model = JournalLine
        fields = ['start_date', 'end_date', 'party__id']


class CreditNoteFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='date_time', lookup_expr='date__gte')
    end_date = filters.DateFilter(field_name='date_time', lookup_expr='date__lte')

    class Meta:
        model = JournalLine
        fields = ['start_date', 'end_date', 'party__id']


class DebitNoteFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='date_time', lookup_expr='date__gte')
    end_date = filters.DateFilter(field_name='date_time', lookup_expr='date__lte')

    class Meta:
        model = JournalLine
        fields = ['start_date', 'end_date', 'party__id']



class JournalEntryFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='date_time', lookup_expr='date__gte')
    end_date = filters.DateFilter(field_name='date_time', lookup_expr='date__lte')

    class Meta:
        model = JournalLine
        fields = ['start_date', 'end_date']