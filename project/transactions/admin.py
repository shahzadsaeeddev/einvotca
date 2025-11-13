from django.contrib import admin
from .models import TaxTransactions, JournalLine, JournalDetail, JournalProductDetail, DayClosing, DayClosingDetail

admin.site.register(TaxTransactions)
@admin.register(JournalLine)
class JournalLineAdmin(admin.ModelAdmin):
    search_fields = ['invoice_no', 'ref_no', 'description', 'party__name', 'payment_method__name']
    list_filter = ['transaction_type', 'transaction_status', 'is_return', 'refunded', 'location__registered_name']
    list_display = ['invoice_no', 'ref_no', 'transaction_type', 'transaction_status', 'party', 'payable_amount', 'paid_amount', 'date_time']


@admin.register(JournalDetail)
class JournalDetailAdmin(admin.ModelAdmin):
    search_fields = ['transaction__invoice_no', 'account_title', 'description']
    list_filter = ['transaction__location__registered_name', 'transaction__transaction_type', 'transaction__transaction_status']
    list_display = ['transaction', 'account_title', 'amount', 'description']


@admin.register(JournalProductDetail)
class JournalProductDetailAdmin(admin.ModelAdmin):
    search_fields = ['invoice__invoice_no', 'item_name']
    list_filter = ['invoice__location__registered_name', 'invoice__transaction_type', 'invoice__transaction_status']
    list_display = (['invoice', 'item_name', 'rate', 'quantity', 'total_inclusive_tax_amount'])


@admin.register(DayClosing)
class DayClosingAdmin(admin.ModelAdmin):
    search_fields = ['closing_balance', 'opening_balance']
    list_filter = ['location__registered_name']
    list_display = ['opening_balance', 'closing_balance', 'sales', 'discount', 'returns']


@admin.register(DayClosingDetail)
class DayClosingDetailAdmin(admin.ModelAdmin):
    search_fields = ['payment_type', 'amount']
    list_filter = ['location__registered_name']
    list_display = ['amount', 'payment_type']




