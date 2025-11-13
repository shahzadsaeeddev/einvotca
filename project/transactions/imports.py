from datetime import timedelta, datetime
from django.db.models.functions import  TruncDay
from django.db.models.query_utils import Q
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Max, Count, Case, Value, CharField, When, F
from accounts.permissions import HasSaleInvoiceRoles, HasCreditNoteRoles, HasPurchaseInvoiceRoles, HasDebitNoteRoles, \
    HasPaymentVoucherRoles, HasReceiptVoucherRoles, HasInventoryReportRoles, HasOutStockReportRoles, \
    HasGeneralJournalReportRoles, HasLegerReportRoles, HasTrailBalanceReportRoles, HasIncomeStatementReportRoles, \
    HasBalanceSheetReportRoles, HasSaleReportRoles, HasPurchaseReportRoles
from neksio_api.tasks import activity_logs_task
from utilities.calculate_dayclosing_total import calculate_day_closing_totals
from .filters import JournalDetailFilter, SaleReportFilter, InventoryReportFilter, SaleInvoiceFilter, PurchaseFilter, \
    DebitNoteFilter, CreditNoteFilter, JournalEntryFilter
from .serializers.TransactionList import *
from .serializers.reports import *
from .serializers.dayClosing import *
from .serializers.common import *
from .serializers.PurchaseTransactions import *
from .serializers.SaleTransactions import *
from .serializers.transactions import *
from rest_framework import generics, permissions, filters, status
from products.models import Categories, ProductItem
from neksio_api.models import Customers, PaymentTypes, InvoiceSettings
from utilities.modelMixins import StandardResultsSetPagination
from neksio_api.serializers.MasterDataSerializers import PaymentTypesSerializer
from neksio_api.serializers.InvoiceSetting import InvoiceLoadSerializer
from neksio_api.models import Parties
from neksio_api.models import FinancialAccounts, AccountSetting

