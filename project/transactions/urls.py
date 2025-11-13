from django.urls import path
from .views import *

app_name = 'transactions'
urlpatterns = [
    path('service-products/', ServiceProductsList.as_view(), name='service-items'),
    path('sales-zatca-resubmit/', SalesZatcaReSubmit.as_view(), name="sale-refund"),

    # --------------------------------------- Manage Sales ------------------------------------------ #

    path('sale-list/', JournalLinesListApiView.as_view(), name="sale"),
    path('sales/', JournalLineMasterCreateApiView.as_view(), name="transactions"),
    path('sale-request/', SaleRequestNumberApiView.as_view(), name="sale-request"),


    path('imei/', IMEINumberApiView.as_view(), name="imei"),

    # -------------------------------------- Manage General View ----------------------------------- #

    path('general-view/<str:slug>/', JournalLinesRetrieveApiView.as_view(), name="general-view"),

    # -------------------------------------- Manage Credit Notes ------------------------------------ #

    path('credit-note-list/', CreditNoteListApiView.as_view(), name="credit-note-list"),
    path('credit-note/', CreditNoteCreateApiView.as_view(), name="credit-note"),

    # --------------------------------------- Manage Purchase -------------------------------------- #

    path('purchase-list/', PurchaseItemsListApiView.as_view(), name="purchase-list"),
    path('purchase/', PurchaseItemsCreateApiView.as_view(), name="purchase"),
    path('purchase-request/', PurchaseRequestNumberApiView.as_view(), name="purchase-request"),

    # --------------------------------------- Manage Debit Notes ---------------------------------- #

    path('debit-note-list/', DebitNoteListApiView.as_view(), name="sale-refund"),
    path('debit-note/', DebitNoteCreateApiView.as_view(), name="sale-refund"),

    # ---------------------------- Manage Payment & Receipt & Journal Entries ------------------- #

    path('journal-entry/', JournalEntryListCreateView.as_view(), name="journal-entry"),
    path('journal-entry/<str:slug>/', JournalEntryRetrieveApiView.as_view(), name="journal-entry"),

    path('payment-entry/', PaymentEntryListCreateView.as_view(), name="payment-entry"),
    path('payment-entry/<str:slug>/', PaymentVoucherRetrieveApiView.as_view(), name="payment-entry"),

    path('receipt-voucher/', ReceiptVoucherEntryListCreateApiView.as_view(), name="receipt-voucher"),

    path('reverse-entries/', ReversePaymentVoucherListCreateView.as_view(), name="reverse-payment-entry"),

    path('opening-balance/', PartyOpeningBalanceCreateApiView.as_view(), name="opening-balance"),

    # ---------------------------------------- Manage Reports ------------------------------------- #

    path('journal-detail/', JournalDetailReportListApiView.as_view(), name="journal-detail"),

    path('trail-balance/', TrialBalanceReportApiView.as_view(), name="trail-balance"),

    path('sale-report/', SaleReportListApiView.as_view(), name="sale-report"),

    path('purchase-report/', PurchaseReportListApiView.as_view(), name="sale-report"),

    path('inventory-report/', InventoryReportListApiView.as_view(), name="inventory-report"),

    path('balance-sheet/', BalanceSheetReportListApiView.as_view(), name="balance-sheet"),

    path('income-statement/', IncomeStatementReportView.as_view(), name="income-statement"),

    path('out-of-stock/', OutOfStockReportView.as_view(), name="out-of-stock"),

    # ------------------------------------------- Dashboard ----------------------------------------- #

    path('request-summary/', DashboardApiView.as_view(), name="request-summary"),

    # ------------------------------------------ Day Closing ---------------------------------------- #

    path('day-closing-summary/', DayClosingSummaryAPIView.as_view(), name="day-closing-summary"),
    path('day-closing-detail/', DayClosingListApiView.as_view(), name="day-closing-detail"),
    path('day-closing/', DayClosingCreateApiView.as_view(), name="day-closing"),






]
