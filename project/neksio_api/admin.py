from django.contrib import admin
from .models import (BusinessTypes, BusinessProfile,
                     BusinessPackages, MediaFiles, PaymentsHistory,
                     Customers, Suppliers, EmailSupport,
                     TaxTypes, Countries, PaymentTypes, InvoiceSettings, BankAccount, Investor, FinancialAccounts,
                     IncomeExpenseHead, AssetLiabilityHead, AccountSetting, Parties, Employees, ActivityLog,
                     BusinessWhatsappProfile, WhatsappContacts)

# Register your models here.

admin.site.site_header = "Einvotca Business Suite"
admin.site.site_title = "Einvotca Admin Panel"
admin.site.index_title = "Welcome to Einvotca Point of Sale"

admin.site.register(BusinessWhatsappProfile)

admin.site.register(EmailSupport)

admin.site.register(BusinessTypes)
admin.site.register(BusinessProfile)
admin.site.register(BusinessPackages)
admin.site.register(MediaFiles)
admin.site.register(TaxTypes)
admin.site.register(Countries)

@admin.register(PaymentsHistory)
class PaymentsHistoryAdmin(admin.ModelAdmin):
    search_fields = ['reference_no', 'amount']
    list_filter = ['business_profile__registered_name']
    list_display = ['reference_no', 'amount', 'orderID', 'paymentID', 'payment_status']

@admin.register(PaymentTypes)
class PaymentTypesAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['location__registered_name']
    list_display = ['name', 'payment_code', 'default_status']


@admin.register(InvoiceSettings)
class InvoiceSettingsAdmin(admin.ModelAdmin):
    search_fields = ['name', 'phone']
    list_filter = ['business__registered_name']
    list_display = ['name', 'address', 'phone', 'tax_no', 'policy', 'default']

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    search_fields = ['account_title']
    list_filter = ['location__registered_name']
    list_display = ['account_title', 'branch_code', 'account_number', 'iban', 'currency']



@admin.register(Investor)
class InvestorAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_filter = ['location__registered_name']
    list_display = ['title', 'is_default', 'equity_percentage']

@admin.register(FinancialAccounts)
class FinancialAccountsAdmin(admin.ModelAdmin):
    search_fields = ['title', 'code']
    list_filter = ['location__registered_name']
    list_display = ['code', 'title', 'type', 'is_sub_ledger_control', ]



@admin.register(IncomeExpenseHead)
class IncomeExpenseHeadAdmin(admin.ModelAdmin):
    search_fields = ['name', 'name', 'type', 'is_active']
    list_filter = ['location__registered_name']
    list_display = ['name', 'type', 'is_active']



@admin.register(AssetLiabilityHead)
class AssetLiabilityHeadAdmin(admin.ModelAdmin):
    search_fields = ['name', 'name', 'type', 'is_active']
    list_filter = ['location__registered_name']
    list_display = ['name', 'type', 'is_active']

admin.site.register(AccountSetting)

@admin.register(Parties)
class PartiesAdmin(admin.ModelAdmin):
    search_fields = ['name', 'email']
    list_filter = ['account_type', 'location__registered_name']
    list_display = ['name', 'email', 'phone', 'address', 'country', 'account_type']


@admin.register(Employees)
class EmployeesAdmin(admin.ModelAdmin):
    search_fields = ['name', 'email']
    list_filter = ['location__registered_name']
    list_display = ['name', 'email', 'phone', 'address', 'salary', 'designation', 'status']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    search_fields = ['action_type', 'module']
    list_filter = ['user__username', 'location__registered_name']
    list_display = ['action_type', 'module', 'description', 'ip_address']


class CustomersAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.filter(account_type='customer')


class SuppliersAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(account_type='supplier')


# Register your models with the custom admin classes
admin.site.register(Customers, CustomersAdmin)
admin.site.register(Suppliers, SuppliersAdmin)
admin.site.register(WhatsappContacts)
