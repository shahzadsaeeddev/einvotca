import uuid

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.postgres.fields import ArrayField
from django.db import models

from neksio_api.models import BusinessProfile, MediaFiles
from zatca_api.models import BusinessLocation

from utilities.modelMixins import ExtraFields, DefaultFilterManager


class RoleGroup(models.Model):
    group_name = models.CharField(max_length=36, blank=False, null=False)
    group_code = models.CharField(max_length=36, blank=False, null=False)
    group_permissions = ArrayField(models.CharField(
        blank=True,
        null=True, max_length=50
    ),
        size=100, default=list
    )
    default_location = models.ForeignKey(BusinessLocation, blank=True, null=True, on_delete=models.SET_NULL)
    visible = models.BooleanField(default=False)

    def __str__(self):
        return self.group_name


class Users(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    """User model."""
    keycloak_uuid = models.CharField(max_length=136, blank=False, null=False)
    is_owner = models.BooleanField(default=False)
    business_profile = models.ForeignKey(BusinessProfile, blank=True, null=True, on_delete=models.SET_NULL)
    default_business_location = models.ForeignKey(BusinessLocation, blank=True, null=True, on_delete=models.SET_NULL)
    collections= models.TextField(blank=True, null=True)
    user_roles = models.ForeignKey(RoleGroup, blank=True, null=True, on_delete=models.SET_NULL)
    neksio_roles = ArrayField(models.CharField(
        blank=True,
        null=True, max_length=50
    ),
        size=100, default=list
    )
    is_delete = models.BooleanField(default=False)
    slug = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.BooleanField(default=True)
    display_picture = models.ForeignKey(MediaFiles, null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def is_manager(self):
        return "PERMISSIONS_CAN_LOGIN" in self.neksio_roles

    # ---------------------------------------------- PERMISSIONS --------------------------------------------------- #

    # ---------------------------------------------- DASHBOARD ----------------------------------------------------- #

    @property
    def view_dashboard(self):
        return "DASHBOARD_VIEW" in self.neksio_roles

    # ---------------------------------------------- PRODUCTS -------------------------------------------------------#

    @property
    def can_view_items(self):
        return "PERMISSION_CAN_VIEW_ITEMS" in self.neksio_roles

    @property
    def can_create_items(self):
        return "PERMISSION_CAN_CREATE_ITEMS" in self.neksio_roles

    @property
    def can_update_items(self):
        return "PERMISSION_CAN_UPDATE_ITEMS" in self.neksio_roles

    @property
    def can_delete_items(self):
        return "PERMISSION_CAN_DELETE_ITEMS" in self.neksio_roles

    # ---------------------------------------------- PRODUCTS ATTRIBUTES -------------------------------------------- #

    @property
    def can_view_items_attribute(self):
        return "PERMISSION_CAN_VIEW_PRODUCT_ATTRIBUTES" in self.neksio_roles

    @property
    def can_create_items_attribute(self):
        return "PERMISSION_CAN_CREATE_PRODUCT_ATTRIBUTES" in self.neksio_roles

    @property
    def can_manage_items_attribute(self):
        return "PERMISSION_CAN_MANAGE_PRODUCT_ATTRIBUTE" in self.neksio_roles

    # ---------------------------------------------- SALE INVOICE -------------------------------------------------- #

    @property
    def can_view_sales(self):
        return "PERMISSION_CAN_VIEW_SALES" in self.neksio_roles

    @property
    def can_create_sales(self):
        return "PERMISSION_CAN_CREATE_SALES" in self.neksio_roles

    # ---------------------------------------------- CREDIT NOTE -------------------------------------------------- #

    @property
    def can_view_credit_notes(self):
        return "PERMISSION_CAN_VIEW_CREDIT_NOTE" in self.neksio_roles

    @property
    def can_create_credit_notes(self):
        return "PERMISSION_CAN_CREATE_CREDIT_NOTE" in self.neksio_roles

    @property
    def can_approve_credit_note(self):
        return "PERMISSION_CAN_APPROVE_CREDIT_NOTE" in self.neksio_roles

    # ---------------------------------------------- PURCHASES -------------------------------------------------- #

    @property
    def can_view_purchases(self):
        return "PERMISSION_CAN_VIEW_PURCHASES" in self.neksio_roles

    @property
    def can_create_purchases(self):
        return "PERMISSION_CAN_CREATE_PURCHASES" in self.neksio_roles

    # ---------------------------------------------- DEBIT NOTE -------------------------------------------------- #

    @property
    def can_view_debit_notes(self):
        return "PERMISSION_CAN_VIEW_DEBIT_NOTE" in self.neksio_roles

    @property
    def can_create_debit_notes(self):
        return "PERMISSION_CAN_CREATE_DEBIT_NOTE" in self.neksio_roles

    @property
    def can_approve_debit_notes(self):
        return "PERMISSION_CAN_APPROVE_DEBIT_NOTE" in self.neksio_roles

    # ---------------------------------------------- PAYMENT VOUCHER ---------------------------------------------- #

    @property
    def can_view_payment_voucher(self):
        return "PERMISSION_CAN_VIEW_PAYMENT_VOUCHER" in self.neksio_roles

    def can_create_payment_voucher(self):
        return "PERMISSION_CAN_CREATE_PAYMENT_VOUCHER" in self.neksio_roles

    # ---------------------------------------------- RECEIPT VOUCHER ---------------------------------------------- #

    @property
    def can_view_receipt_voucher(self):
        return "PERMISSION_CAN_VIEW_RECEIPT_VOUCHER" in self.neksio_roles

    @property
    def can_create_receipt_voucher(self):
        return "PERMISSION_CAN_CREATE_RECEIPT_VOUCHER" in self.neksio_roles

    @property
    def can_approve_receipt_voucher(self):
        return "PERMISSION_CAN_REVERSE_RECEIPT_VOUCHER" in self.neksio_roles


    # --------------------------------------------- DAY CLOSING ---------------------------------------------------- #

    @property
    def can_view_day_closing(self):
        return "PERMISSION_CAN_VIEW_DAY_CLOSING" in self.neksio_roles

    @property
    def can_create_day_closing(self):
        return "PERMISSION_CAN_CREATE_DAY_CLOSING" in self.neksio_roles

    # ---------------------------------------------- CUSTOMERS ----------------------------------------------------- #

    @property
    def can_view_customers(self):
        return "PERMISSION_CAN_VIEW_CUSTOMERS" in self.neksio_roles

    @property
    def can_create_customers(self):
        return "PERMISSION_CAN_CREATE_CUSTOMERS" in self.neksio_roles

    @property
    def can_manage_customers(self):
        return "PERMISSION_CAN_MANAGE_CUSTOMERS" in self.neksio_roles

    # ---------------------------------------------- SUPPLIERS ----------------------------------------------------- #

    @property
    def can_view_suppliers(self):
        return "PERMISSION_CAN_VIEW_SUPPLIERS" in self.neksio_roles

    @property
    def can_create_suppliers(self):
        return "PERMISSION_CAN_CREATE_SUPPLIERS" in self.neksio_roles

    @property
    def can_manage_suppliers(self):
        return "PERMISSION_CAN_MANAGE_SUPPLIERS" in self.neksio_roles

    # ---------------------------------------------- INVESTORS ----------------------------------------------------- #

    @property
    def can_view_investors(self):
        return "PERMISSION_CAN_VIEW_INVESTORS" in self.neksio_roles

    @property
    def can_create_investors(self):
        return "PERMISSION_CAN_CREATE_INVESTORS" in self.neksio_roles

    @property
    def can_manage_investors(self):
        return "PERMISSION_CAN_MANAGE_INVESTORS" in self.neksio_roles

    # ---------------------------------------------- BANKS ----------------------------------------------------- #

    @property
    def can_view_banks(self):
        return "PERMISSION_CAN_VIEW_BANKS" in self.neksio_roles

    @property
    def can_create_banks(self):
        return "PERMISSION_CAN_CREATE_BANKS" in self.neksio_roles

    @property
    def can_manage_banks(self):
        return "PERMISSION_CAN_MANAGE_BANKS" in self.neksio_roles

    # ---------------------------------------------- FINANCIAL ACCOUNTS -------------------------------------------- #

    @property
    def can_view_financial_accounts(self):
        return "PERMISSION_CAN_VIEW_FINANCIAL_ACCOUNTS" in self.neksio_roles

    @property
    def can_create_financial_accounts(self):
        return "PERMISSION_CAN_CREATE_FINANCIAL_ACCOUNTS" in self.neksio_roles

    @property
    def can_manage_financial_accounts(self):
        return "PERMISSION_CAN_MANAGE_FINANCIAL_ACCOUNTS" in self.neksio_roles

    # ---------------------------------------------- EMPLOYEES ----------------------------------------------------- #

    @property
    def can_view_employees(self):
        return "PERMISSION_CAN_VIEW_EMPLOYEES" in self.neksio_roles

    @property
    def can_create_employees(self):
        return "PERMISSION_CAN_CREATE_EMPLOYEES" in self.neksio_roles

    @property
    def can_manage_employees(self):
        return "PERMISSION_CAN_MANAGE_EMPLOYEES" in self.neksio_roles

    # ---------------------------------------------- INCOME EXPENSE ------------------------------------------------ #

    @property
    def can_view_income_expense(self):
        return "PERMISSION_CAN_VIEW_INCOME_EXPENSE" in self.neksio_roles

    @property
    def can_create_income_expense(self):
        return "PERMISSION_CAN_CREATE_INCOME_EXPENSE" in self.neksio_roles

    @property
    def can_manage_income_expense(self):
        return "PERMISSION_CAN_MANAGE_INCOME_EXPENSE" in self.neksio_roles

    # ---------------------------------------------- ASSET LIABILITY ----------------------------------------------- #

    @property
    def can_view_liability(self):
        return "PERMISSION_CAN_VIEW_LIABILITY" in self.neksio_roles

    @property
    def can_create_liability(self):
        return "PERMISSION_CAN_CREATE_LIABILITY" in self.neksio_roles

    @property
    def can_manage_liability(self):
        return "PERMISSION_CAN_MANAGE_LIABILITY" in self.neksio_roles

    # ---------------------------------------------- REPORTS ----------------------------------------------------- #

    @property
    def can_view_inventory_report(self):
        return "PERMISSION_CAN_VIEW_INVENTORY_REPORT" in self.neksio_roles

    @property
    def can_view_stock_adjustment(self):
        return "PERMISSION_CAN_VIEW_STOCK_ADJUSTMENT_REPORT" in self.neksio_roles

    @property
    def can_view_out_stock_report(self):
        return "PERMISSION_CAN_VIEW_OUT_STOCK_REPORT" in self.neksio_roles

    @property
    def can_view_general_journal(self):
        return "PERMISSION_CAN_VIEW_GENERAL_JOURNAL_REPORT" in self.neksio_roles

    @property
    def can_view_leger_report(self):
        return "PERMISSION_CAN_VIEW_LEGER_REPORT" in self.neksio_roles

    @property
    def trail_balance_report(self):
        return "PERMISSION_CAN_VIEW_TRAIL_BALANCE_REPORT" in self.neksio_roles

    @property
    def can_view_income_statement_report(self):
        return "PERMISSION_CAN_VIEW_INCOME_STATEMENT_REPORT" in self.neksio_roles

    @property
    def can_view_balance_sheet(self):
        return "PERMISSION_CAN_VIEW_BALANCE_SHEET_REPORT" in self.neksio_roles

    @property
    def can_view_sale_report(self):
        return "PERMISSION_CAN_VIEW_SALE_REPORT" in self.neksio_roles

    @property
    def can_view_purchase_report(self):
        return "PERMISSION_CAN_VIEW_PURCHASE_REPORT" in self.neksio_roles

    # ---------------------------------------------- BUSINESS PROFILE ---------------------------------------------- #

    @property
    def can_view_business_profile(self):
        return "PERMISSION_CAN_VIEW_BUSINESS_PROFILE" in self.neksio_roles

    @property
    def can_manage_business_profile(self):
        return "PERMISSION_CAN_UPDATE_BUSINESS_PROFILE" in self.neksio_roles

    # ---------------------------------------------- INVOICE SETUP ------------------------------------------------- #

    @property
    def can_view_invoice_setup(self):
        return "PERMISSION_CAN_VIEW_INVOICE_SETUP" in self.neksio_roles

    @property
    def can_create_invoice_setup(self):
        return "PERMISSION_CAN_CREATE_INVOICE_SETUP" in self.neksio_roles

    @property
    def can_manage_invoice_setup(self):
        return "PERMISSION_CAN_MANAGE_INVOICE_SETUP" in self.neksio_roles

    # ---------------------------------------------- USERS ----------------------------------------------------- #

    @property
    def can_view_users(self):
        return "PERMISSION_CAN_VIEW_USERS" in self.neksio_roles

    @property
    def can_create_users(self):
        return "PERMISSION_CAN_CREATE_USERS" in self.neksio_roles

    @property
    def can_manage_users(self):
        return "PERMISSION_CAN_MANAGE_USERS" in self.neksio_roles

    # ---------------------------------------------- DINING TABLE ----------------------------------------------------- #

    @property
    def can_view_dining(self):
        return "PERMISSION_CAN_VIEW_DINING_TABLES" in self.neksio_roles

    @property
    def can_create_dining(self):
        return "PERMISSION_CAN_CREATE_DINING_TABLES" in self.neksio_roles

    @property
    def can_manage_dining(self):
        return "PERMISSION_CAN_MANAGE_DINING_TABLES" in self.neksio_roles

    # ---------------------------------------------- ACCOUNT SETTING ------------------------------------------------ #

    @property
    def can_view_account_settings(self):
        return "PERMISSION_CAN_VIEW_ACCOUNT_SETTING" in self.neksio_roles

    @property
    def can_view_activity_logs(self):
        return "PERMISSION_CAN_VIEW_ACTIVITY_LOGS" in self.neksio_roles






class MasterAccounts(ExtraFields):
    account_name = models.CharField(max_length=50)
    choice = (('customer', 'Customer'), ('supplier', 'Supplier'),
              ('employee', 'Employee'), ('financial', 'Financial')
              , ('banks', 'Banks'), ('other', 'Other'))
    account_type = models.CharField(max_length=30, choices=choice)
    description = models.CharField(blank=True, max_length=250)
    location = models.ForeignKey('zatca_api.BusinessLocation', on_delete=models.SET_NULL, blank=True, null=True,
                                 related_name="location_accounts")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    objects = DefaultFilterManager()

    def __str__(self):
        return self.account_name


class PartiesAccounts(MasterAccounts):
    schemeID = models.CharField(max_length=5, blank=True, verbose_name="Scheme ID")
    schemeNo = models.BigIntegerField(blank=True, null=True, verbose_name="Scheme Number")
    streetName = models.CharField(max_length=50, blank=True, verbose_name="Street Name")
    buildingNumber = models.CharField(max_length=50, blank=True, verbose_name="Building Number")
    plotIdentification = models.CharField(max_length=50, blank=True, verbose_name="Plot Identification")
    citySubdivisionName = models.CharField(max_length=50, blank=True, verbose_name="City Subdivision Name")
    cityName = models.CharField(max_length=50, blank=True, verbose_name="City Name")
    postalZone = models.CharField(max_length=10, blank=True, verbose_name="Postal Zone")
    country = models.CharField(max_length=2, blank=True, verbose_name="Country")
    companyTaxNo = models.BigIntegerField(blank=True, null=True, verbose_name="Company Tax No")
    taxScheme = models.CharField(max_length=5, blank=True, verbose_name="Tax Scheme")
    registrationName = models.CharField(max_length=60, blank=True, verbose_name="Registration Name")

    def __str__(self):
        return f"{self.schemeID} - {self.registrationName}"
