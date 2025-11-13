from django_filters import rest_framework as filters

from transactions.models import JournalDetail
from .models import PaymentsHistory, MediaFiles, IncomeExpenseHead, ActivityLog


class PaymentFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='created',
                                    lookup_expr='gte')
    end_date = filters.DateFilter(field_name='created',
                                  lookup_expr='lte')
    paid_by__slug = filters.CharFilter(field_name='paid_by__slug')  # Assuming createdBy is a CharField
    payment_status = filters.CharFilter(field_name='payment_status')  # Replace with the correct field name

    class Meta:
        model = PaymentsHistory
        fields = ['start_date', 'end_date', 'paid_by__slug', 'payment_status']


class MediaFilter(filters.FilterSet):
    class Meta:
        model = MediaFiles
        fields = ['file_type']


class IncomeExpenseFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='created_at__date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='created_at__date', lookup_expr='lte')
    class Meta:
        model = IncomeExpenseHead
        fields = ['start_date', 'end_date', 'type']

class ActivityLogsFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='created_at__date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='created_at__date', lookup_expr='lte')
    class Meta:
        model = ActivityLog
        fields = ['start_date', 'end_date']


class BankTransactionFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='transaction__date_time__date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='transaction__date_time__date', lookup_expr='lte')
    type = filters.CharFilter(field_name='transaction__transaction_type', lookup_expr='exact')

    class Meta:
        model = JournalDetail
        fields = ['start_date', 'end_date', 'type']
