from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.utils.text import slugify
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import filters
import os
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.keycloak import update_role
from .filters import PaymentFilter, MediaFilter, IncomeExpenseFilter, ActivityLogsFilter, BankTransactionFilter
from .paypal_sdk import get_paypal_access_token
import requests
from rest_framework import permissions
from rest_framework import generics
from .models import *
from .serializers.Employees import *
from .serializers.FinancialAccounts import *
from .serializers.CustomerSupplier import *
from .serializers.AssetLiabilityIncomeExpense import *
from .serializers.BusinessProfile import *
from .serializers.BankAccounts import *
from .serializers.Investors import *
from .serializers.InvoiceSetting import *
from .serializers.MasterDataSerializers import *
from .serializers.Whatsapp import *
from django.shortcuts import redirect
from accounts.permissions import HasRolesManager, HasCustomersRoles, HasSuppliersRoles, HasInvestorsRoles, \
    HasBankAccountsRoles, HasFinancialAccountsRoles, HasEmployeesRoles, HasIncomeExpenseRoles, HasAssetLiabilityRoles, \
    HasBusinessProfileRoles, HasAccountSettingRoles, HasInvoiceSetupRoles, HasActivityLogsRoles

from invoices.models import ZatcaInvoicesProduction

from django.conf import settings
from datetime import datetime

from transactions.models import JournalLine

from transactions.models import JournalDetail
from .tasks import activity_logs_task

BOT_URL = os.getenv('BOT_URL')
BOT_KEY = os.getenv('BOT_KEY')
WEB_HOOK_URL = os.getenv('WEB_HOOK_URL')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000