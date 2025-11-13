from django.urls import path

from .views import *

urlpatterns = [

    path('business-types/', BusinessTypesView.as_view(), name="business-types"),

    # ---------------------------------- Manage Business Profile ---------------------------- #

    path('business/profile/', BusinessProfileRetrieveView.as_view(), name="business-profile"),
    path('business/whatsapp/', BusinessWhatsappApiView.as_view(), name="whatsapp-profile"),
    path('business/facebook/', FacebookWebhookApiView.as_view(), name="facebook-profile"),
    path('business/token/', BusinessProfileSecretView.as_view(), name="business-token"),
    path('business-profile/', BusinessProfileView.as_view(), name="business-profile"),
    path('business/payments/', BusinessPaymentsView.as_view(), name="business-profile"),

    path('current-plan/', CurrentPackagePlanView.as_view(), name="current-plan"),

    path('business/current/bill/', BusinessCurrentBillView.as_view(), name="current-bill"),

    # ------------------------------- Manage Media Files -------------------------------------- #

    path('media/', MediaFilesView.as_view(), name="media-files"),
    path('media/<str:slug>/', MediaFilesDetailView.as_view(), name="media-files"),

    path('package-planes/', BusinessPackagesView.as_view(), name="package-planes"),

    path('support/', EmailSupportView.as_view(), name="support"),

    path('countries/', CountriesView.as_view(), name="countries"),

    path('taxes/', TaxTypeView.as_view(), name="taxes"),

    path('payment-methods/', PaymentTypeView.as_view(), name="payment-methods"),

    # ------------------------------ Manage Customers ------------------------------------------ #

    path('customers/', CustomersView.as_view(), name="customers"),
    path('customer-report/', CustomerReportView.as_view(), name="customer-report"),
    path('customers/<str:slug>/', CustomersDetailView.as_view(), name="customers-details"),
    path('customer-details/', CustomerDetailListApiView.as_view(), name="supplier-details"),

    path('customer-supplier/', CustomerSupplierApiView.as_view(), name="customer-supplier"),


    path('payment-detail/', CustomerSupplierPaymentListAPIView.as_view(), name="payment-detail"),

    # -------------------------------- Manage Suppliers --------------------------------------- #

    path('supplier-details/', SupplierDetailListApiView.as_view(), name="supplier-details"),
    path('suppliers/', SuppliersView.as_view(), name="suppliers"),
    path('supplier-report/', SupplierReportView.as_view(), name="suppliers"),
    path('suppliers/<str:slug>/', SuppliersDetailView.as_view(), name="suppliers-details"),

    path('invoice-setting/', InvoiceSettingView.as_view(), name="invoice-setting"),
    path('invoice-setting/<str:id>/', InvoiceSettingDetailView.as_view(), name="invoice-setting-details"),

    # --------------------------------- Manage Paypal ---------------------------------------- #

    path('paypal-order/', CreateOrderView.as_view(), name="paypal-order"),
    path('capture-paypal/', CapturePaypalView.as_view(), name="capture-paypal"),

    path('payment-history/', PaymentHistoryListApiView.as_view(), name="payment-history"),

    # --------------------------------- Manage Banks ----------------------------------------- #

    path('bank-account/', BankInformationListCreateApiView.as_view(), name="bank-information"),
    path('bank-report/', BankBalanceReportView.as_view(), name="bank-report"),
    path('bank-history/<str:pk>/', BankTransactionHistoryView.as_view(), name="bank-account-history"),
    path('bank-account/<str:slug>/', BankInformationRetrieveUpdateDeleteApiView.as_view(),
         name="bank-information-update"),

    # ---------------------------------- Manage Investors ------------------------------------ #

    path('investor/', InvestorListCreateApiView.as_view(), name="investor"),
    path('investor-report/', InvestorReportApiView.as_view(), name="investor-report"),
    path('investor/<str:slug>/', InvestorRetrieveUpdateDeleteApiView.as_view(), name="investor-update"),

    # ---------------------------------- Manage Chart Of Accounts ----------------------------- #

    path('financial-accounts/', FinancialAccountsListCreateApiView.as_view(), name="financial-accounts"),
    path('financial-account-master/', FinancialAccountsListApiView.as_view(), name="financial-account-master"),
    path('financial-accounts/<str:slug>/', FinancialAccountsRetrieveUpdateDeleteApiView.as_view(),
         name="financial-accounts-update"),
    path('financial-account-detail/', FinancialAccountsChildApiView.as_view(), name="chart-account-detail"),

    path('payable-accounts/', PayableAccountsApiView.as_view(), name="payable-accounts"),

    path('account-type/', FinancialAccountListAPIView.as_view(), name="account-type"),

    path('opening-balance-account/', OpeningBalanceAccountListApiView.as_view(), name="opening-balance-account"),

    path('invoice-serial/', FinancialAccountCodeGenerateAPIView.as_view(), name="invoice-serial"),

    # ----------------------------------- Manage Income Expenses -------------------------------- #

    path('income-expenses/', IncomeExpenseHeadListCreateApiView.as_view(), name="income-expenses"),
    path('income-expenses/<str:slug>/', IncomeExpenseHeadRetrieveUpdateDeleteApiView.as_view(),
         name="income-expenses-update"),

    # ----------------------------------- Manage Liabilities ------------------------------------- #

    path("liability-accounts/", LiabilityAccountsApiView.as_view(), name="liability-accounts"),
    path('asset-liability/', AssestLiabilityHeadListCreateApiView.as_view(), name="assest-liability"),
    path('asset-liability/<str:slug>/', AssestLiabilityHeadRetrieveUpdateDeleteApiView.as_view(),
         name="assest-liability-update"),

    # ----------------------------------- Manage Accounts Setting --------------------------------- #

    path('account-setting/', AccountSettingListUpdateApiView.as_view(), name="account-setting-list"),

    # ----------------------------------- Manage Account Setting ----------------------------------- #

    path('employees/', EmployeeListCreateApiView.as_view(), name="employees"),
    path('employees-report/', EmployeeReportApiView.as_view(), name="employees-report"),
    path('employees/<str:slug>/', EmployeeRetrieveUpdateDeleteApiView.as_view(), name="employee-update"),

    # ----------------------------------- Activity Logs --------------------------------------------- #

    path('activity-logs/', ActivityLogsListApiView.as_view(), name="activity-logs"),

    path('create-instance/', WhatsAppIntegrationListCreateApiView.as_view(), name="create-instance"),
    path('connect-instance/', ConnectInstanceApiView.as_view(), name="connect-instance"),
    path('connection-state/', ConnectStatusApiView.as_view(), name="connection-state"),
    path('instance-detail/', GetWhatsappProfileApiView.as_view(), name="instance-detail"),
    # path('logout/', LogoutWhatsappProfileApiView.as_view(), name="logout"),

    path('set-webhook/', SetWebHookApiView.as_view(), name="set-webhook"),

    path('import-contacts/', ContactImportView.as_view(), name="import-contacts"),
    path('contacts/', WhatsAppContactCreateApiView.as_view(), name="contact-list"),

    path('contacts/<str:pk>/', WhatsAppContactUpdateDeleteApiView.as_view(), name="contact-update"),

    path('bulk-send/', SendMessageContactsView.as_view(), name="bulk-send"),

]
