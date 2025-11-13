import logging
import uuid
import random
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


from utilities.modelMixins import (TimestampMixin, ExtraFields,
                                   CustomerFilterManager, SupplierFilterManager)
from neksio_api.charts_data import create_financial_accounts
from products.models import UnitOfMeasurement, Categories
from products.models import ProductItem, PromoCodes, SalePriceSlot


class DefaultManager(models.Manager):
    def by_location(self, user):
        return self.filter(location=user.business_profile)


class BusinessTypes(models.Model):
    slug = models.SlugField(unique=True, default=uuid.uuid4, editable=False)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(blank=True, max_length=230)
    description = ArrayField(models.CharField(
        blank=True,
        null=True, max_length=50
    ),
        size=50, default=list
    )
    description_ar = ArrayField(models.CharField(
        blank=True,
        null=True, max_length=50
    ),
        size=50, default=list
    )
    url = models.CharField(blank=True, max_length=230)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name


class Countries(TimestampMixin):
    name = models.CharField(max_length=30)
    slug = models.SlugField(unique=True, default=uuid.uuid4)
    short_name = models.CharField(max_length=30)
    country_code = models.CharField(max_length=6)
    disabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Bank(models.Model):
    name = models.CharField(max_length=255)
    swift_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.ForeignKey(Countries, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class MediaFiles(ExtraFields):
    file_name = models.CharField(blank=True, max_length=230)
    file = models.FileField(upload_to='static/uploads/')
    choice = (
        ("image", "image"),
        ("pdf", "pdf"),
        ("icons", "icons"),
        ("other", "other")

    )
    file_type = models.CharField(blank=True, max_length=30, choices=choice)
    alt_text = models.CharField(blank=True, max_length=150)
    description = models.CharField(blank=True, max_length=250)
    thumbnail = models.ImageField(upload_to='static/uploads/thumbnail/', blank=True, null=True)
    objects = DefaultManager()

    def __str__(self):
        return self.file_name


class BusinessPackages(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, default=uuid.uuid4, editable=False)
    package_name = models.CharField(blank=True, max_length=230)
    discount = models.PositiveIntegerField(default=0)
    discount_percentage = models.PositiveIntegerField(default=0)
    location_price = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    default_package = models.BooleanField()
    package_code = models.CharField(blank=True, max_length=150)
    services = ArrayField(models.CharField(
        blank=True,
        null=True, max_length=50
    ),
        size=50, default=list
    )
    locations = models.PositiveIntegerField(default=0)
    users = models.PositiveIntegerField(default=0)
    ordering = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(null=True, blank=True)
    details = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['ordering']

    def __str__(self):
        return self.package_name


class BusinessProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, default=uuid.uuid4, editable=False)
    registered_name = models.CharField(blank=True, max_length=230)
    poc_full_name = models.CharField(blank=True, max_length=230)
    country = models.ForeignKey(Countries, on_delete=models.SET_NULL, null=True)
    phone = models.CharField(blank=True, max_length=230)
    alt_phone = models.CharField(blank=True, max_length=230)
    tax_no = models.CharField(blank=True, max_length=16)
    registered_address = models.CharField(blank=True, max_length=230)
    business_category = models.CharField(blank=True, max_length=230)
    support_pin = models.CharField(blank=True, max_length=230)
    business_type = models.ForeignKey(BusinessTypes, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name="business_type")
    package_plan = models.ForeignKey(BusinessPackages, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="business_profile")
    account_end_date = models.DateTimeField()
    no_of_locations = models.PositiveIntegerField(default=1)
    no_of_users = models.PositiveIntegerField(default=3)
    expiry_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.registered_name

class BusinessWhatsappProfile(models.Model):
    business_profile = models.OneToOneField(BusinessProfile, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name="business_whatsapp_profile")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collections = models.CharField(max_length=100, null=True, blank=True)
    business_name = models.CharField(max_length=255, null=True, blank=True)
    business_email = models.EmailField(null=True, blank=True)
    manager_id = models.CharField(max_length=50, null=True, blank=True)  # If this refers to an external manager ID
    whatsapp_phone = models.CharField(max_length=20, null=True, blank=True)
    whatsapp_account_id = models.CharField(max_length=100, blank=True, null=True)
    authorize = models.BooleanField(default=False)
    authorize_key = models.CharField(max_length=250, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    admin_phone = models.CharField(max_length=20, blank=True)
    whatsapp_integration = models.CharField(max_length=100, blank=True)
    instance_name = models.CharField(max_length=255, blank=True)
    qrcode = models.BooleanField(default=False)
    data_collection = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.instance_name} ({self.phone_number})"



class WhatsappContacts(ExtraFields):
    connection = models.ForeignKey(BusinessWhatsappProfile, on_delete=models.CASCADE, related_name='profile', null=True,
                                   blank=True)
    number = models.CharField(max_length=120, null=True, blank=True)
    name = models.CharField(max_length=120, null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.name


class PaymentsHistory(TimestampMixin):
    reference_no = models.CharField(blank=True, max_length=100)
    slug = models.UUIDField(default=uuid.uuid4, editable=False)
    package_plan = models.ForeignKey(BusinessPackages, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="current_package")
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name="business_history")
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    paid_by = models.ForeignKey('accounts.Users', on_delete=models.SET_NULL, null=True, verbose_name="payments")
    choice = (('pending', 'pending'), ('declined', 'declined'), ('success', 'success'))
    payment_status = models.CharField(max_length=20, choices=choice)
    orderID = models.CharField(max_length=100, null=True, blank=True)
    payerID = models.CharField(max_length=100, null=True, blank=True)
    paymentID = models.CharField(max_length=100, null=True, blank=True)
    billingToken = models.CharField(max_length=100, blank=True, null=True)
    facilitatorAccessToken = models.CharField(max_length=200, blank=True, null=True)
    paymentSource = models.CharField(max_length=100, blank=True, null=True)
    duration = models.PositiveIntegerField(null=True, blank=True)


# Create your models here.
class DummyData(models.Model):
    """User model."""
    record_name = models.CharField(max_length=36, blank=False, null=False)
    record_number = models.PositiveIntegerField(default=0)
    record_status = models.BooleanField()

    def __str__(self):
        return self.record_name


def ticket_no():
    return '{:08d}'.format(random.randint(0, 99999999))


class EmailSupport(TimestampMixin):
    type_choices = ((1, 'Sales'), (2, 'After Sales'), (3, 'Technical Support'), (4, 'Advanced Support')
                        , (5, 'Bugs'), (6, 'Enhancement'))
    support_type = models.CharField(max_length=40, choices=type_choices)
    ticket_no = models.CharField(unique=False, default=ticket_no, editable=False)
    slug = models.SlugField(unique=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    phone = models.CharField(max_length=16)
    subject = models.CharField(max_length=60)
    message = models.TextField()
    status_choices = ((1, 'Pending'), (2, 'In Progress'), (3, 'Resolved'), (4, 'Not Resolved'))
    status = models.CharField(max_length=20, choices=status_choices, default="Pending")
    created_by = models.ForeignKey('accounts.Users', on_delete=models.SET_NULL, null=True)
    resolved_by = models.ForeignKey('accounts.Users', related_name="tickets", on_delete=models.SET_NULL, null=True)
    is_external = models.BooleanField(default=False)

    def __str__(self):
        return "Subject: {}, Status:{} ".format(
            self.subject, self.status)


class FinancialAccounts(ExtraFields):
    ACCOUNT_TYPE_CHOICES = [
        ('Asset', 'Asset'),
        ('Liability', 'Liability'),
        ('Equity', 'Equity'),
        ('Revenue', 'Revenue'),
        ('CGS', 'Cost of Goods Sold'),
        ('Expense', 'Expense')
    ]
    code = models.CharField(max_length=10)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    is_sub_ledger_control = models.BooleanField(default=False)
    sub_ledger_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="E.g., 'supplier', 'customer', etc."
    )
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='children')
    is_ordinary = models.BooleanField(default=False)
    objects = DefaultManager()

    def __str__(self):
        return f"{self.code} - {self.title} ({self.type})"


class TaxTypes(ExtraFields):
    name = models.CharField(blank=True, max_length=230)
    description = models.TextField(null=True, blank=True)
    tax_percent = models.DecimalField(max_digits=2, decimal_places=0, null=True, blank=True)
    default_status = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class PaymentTypes(ExtraFields):
    name = models.CharField(max_length=30)
    payment_code = models.CharField(max_length=3)
    default_status = models.BooleanField(default=False)
    chart_of_account = models.ForeignKey(FinancialAccounts, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='payments')

    class Meta:
        ordering = ['-default_status']

    def __str__(self):
        return self.name


class Parties(ExtraFields):
    ACCOUNT_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('supplier', 'Supplier'),
        ('both', 'Both')
    ]

    account_type = models.CharField(
        max_length=50,
        verbose_name="Account Type",
        choices=ACCOUNT_TYPE_CHOICES,
        blank=True,
        null=True
    )
    chart_of_account = models.OneToOneField(
        FinancialAccounts,
        on_delete=models.PROTECT, null=True, blank=True)

    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    # Legal and business info
    tax_id = models.CharField(max_length=100, blank=True, null=True)
    taxable = models.BooleanField(default=False, verbose_name="Taxable")
    photo = models.ForeignKey('MediaFiles', verbose_name="Photo", null=True, blank=True, on_delete=models.SET_NULL)
    national_id = models.CharField(max_length=100, blank=True, null=True)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    business_type = models.CharField(max_length=100, blank=True, null=True)

    # Financial and banking info
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=100, blank=True, null=True)
    iban = models.CharField(max_length=100, blank=True, null=True)
    swift_code = models.CharField(max_length=50, blank=True, null=True)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)

    # Misc
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    SCHEMA_CHOICES = [
        ('TIN', 'TIN'), ('GCC', 'GCC'), ('IQA', 'IQA'), ('PAS', 'PAS'),
        ('CRN', 'CRN'), ('MOM', 'MOM'), ('MLS', 'MLS'),
        ('700', '700'), ('SAG', 'SAG'), ('OTH', 'OTH')
    ]
    scheme_type = models.CharField(max_length=50, verbose_name="Scheme ID", choices=SCHEMA_CHOICES, null=True,
                                   blank=True, default="CRN")
    scheme_no = models.BigIntegerField(verbose_name="Scheme Number", null=True, blank=True)
    street_name = models.CharField(max_length=255, verbose_name="Street Name", blank=True, null=True)
    building_number = models.CharField(max_length=50, verbose_name="Building Number", blank=True, null=True)
    plot_identification = models.CharField(max_length=50, verbose_name="Plot Identification", blank=True, null=True)
    city_subdivision_name = models.CharField(max_length=255, verbose_name="City Subdivision Name", blank=True,
                                             null=True)
    city_name = models.CharField(max_length=255, verbose_name="City Name", blank=True, null=True)
    postal_zone = models.CharField(max_length=50, verbose_name="Postal Zone", blank=True, null=True)
    tax_scheme = models.CharField(max_length=50, verbose_name="Tax Type", blank=True, null=True, default='VAT')
    registration_name = models.CharField(max_length=255, verbose_name="Registration Name", blank=True, null=True)
    xml_data = models.TextField(verbose_name="XML Data", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.account_type or 'N/A'})"


class Customers(Parties):
    objects = CustomerFilterManager()

    class Meta:
        proxy = True
        verbose_name = "customer"
        verbose_name_plural = "customers"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.account_type = 'customer'
        super().save(*args, **kwargs)


class Suppliers(Parties):
    objects = SupplierFilterManager()

    class Meta:
        proxy = True
        verbose_name = "supplier"
        verbose_name_plural = "suppliers"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.account_type = 'supplier'
        super().save(*args, **kwargs)


class BankAccount(ExtraFields):
    chart_of_account = models.OneToOneField(
        FinancialAccounts,
        on_delete=models.PROTECT, null=True, blank=True,
        limit_choices_to=models.Q(type='Asset'), related_name='bank_account',
    )

    account_title = models.CharField(max_length=255)
    branch_code = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=100, null=True, blank=True)
    iban = models.CharField(max_length=34, blank=True, null=True)
    currency = models.CharField(max_length=10, default="SAR")
    objects = DefaultManager()

    def __str__(self):
        return f" - {self.account_title}"


class Investor(ExtraFields):
    chart_of_account = models.ForeignKey(FinancialAccounts, on_delete=models.PROTECT, null=True, blank=True,
                                         related_name='investor')
    name = models.ForeignKey(Bank, on_delete=models.CASCADE, null=True, blank=True, related_name='investor_name')
    title = models.CharField(max_length=255, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    equity_percentage = models.PositiveIntegerField(default=0)
    objects = DefaultManager()

    # def __str__(self):
    #     return f"{self.account_holder_name} - {self.account_number}"


class IncomeExpenseHead(ExtraFields):
    HEAD_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense')
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=HEAD_TYPES)
    chart_of_account = models.ForeignKey(FinancialAccounts, on_delete=models.PROTECT, null=True, blank=True,
                                         limit_choices_to=models.Q(type='Expense') | models.Q(type='Revenue'),
                                         related_name='income_expense_head')
    is_active = models.BooleanField(default=True)
    objects = DefaultManager()

    def __str__(self):
        return f"{self.name} ({self.type})"


class AssetLiabilityHead(ExtraFields):
    HEAD_TYPES = [
        ('asset', 'Asset'),
        ('liability', 'Liability')
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=HEAD_TYPES)
    chart_of_account = models.ForeignKey(FinancialAccounts, on_delete=models.PROTECT, null=True, blank=True,
                                         limit_choices_to=models.Q(type='Asset') | models.Q(type='Liability'),
                                         related_name='asset_liability_head')
    is_active = models.BooleanField(default=True)
    objects = DefaultManager()

    def __str__(self):
        return f"{self.name} ({self.type})"


class Employees(ExtraFields):
    chart_of_account = models.ForeignKey(FinancialAccounts, on_delete=models.PROTECT, null=True, blank=True,
                                          related_name='employees')
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Employee Name")
    phone = models.CharField(max_length=100, null=True, blank=True, verbose_name="Contact Number")
    email = models.CharField(max_length=100, null=True, blank=True, verbose_name="Email")
    address = models.TextField(max_length=100, null=True, blank=True, verbose_name="Address")
    designation = models.CharField(max_length=100, null=True, blank=True, verbose_name="Employee Designation")
    salary = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Salary")
    status = models.BooleanField(default=False, help_text="Set to true if the employee is active.")
    objects = DefaultManager()

    class Meta:
        verbose_name = "employee"
        verbose_name_plural = "employees"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.chart_of_account.title}"


class InvoiceSettings(TimestampMixin):
    name = models.CharField(blank=True, max_length=150, null=True)
    address = models.CharField(blank=True, max_length=500, null=True)
    phone = models.CharField(blank=True, max_length=20, null=True)
    tax_no = models.CharField(blank=True, max_length=16, null=True)
    logo = models.ForeignKey(MediaFiles, verbose_name="Photo", null=True, blank=True, on_delete=models.SET_NULL)
    policy = models.CharField(blank=True, max_length=500, null=True)
    policy_ar = models.CharField(blank=True, max_length=500, null=True)
    business = models.ForeignKey(BusinessProfile, verbose_name="business_invoice", null=True, blank=True,
                                 on_delete=models.SET_NULL)
    branch = models.ManyToManyField('zatca_api.BusinessLocation', verbose_name="branch_invoice", blank=True)
    default = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at', 'default']

    def __str__(self):
        return f"Address for {self.name} in {self.tax_no}"


class AccountSetting(TimestampMixin):
    location = models.OneToOneField(BusinessProfile, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='account_setting')
    cash_account = models.CharField(max_length=250, verbose_name="cash", null=True, blank=True)
    inventory = models.CharField(max_length=250, verbose_name="inventory", null=True, blank=True)
    banks = models.CharField(max_length=250, verbose_name="banks", null=True, blank=True)
    equity = models.CharField(max_length=250, verbose_name='Equity', null=True, blank=True)
    income = models.CharField(max_length=250, verbose_name="income", null=True, blank=True)
    expense = models.CharField(max_length=250, verbose_name="expense", null=True, blank=True)
    receive_account = models.CharField(max_length=250, verbose_name="account receive able", null=True, blank=True)
    payable_account = models.CharField(max_length=250, verbose_name="account payable", null=True, blank=True)
    profit_loss = models.CharField(max_length=250, verbose_name="profit and loss", null=True, blank=True)
    tax = models.CharField(max_length=250, verbose_name="Tax", null=True, blank=True)
    other = models.CharField(max_length=250, verbose_name="others", null=True, blank=True)
    stock_receive = models.CharField(max_length=250, verbose_name="Stock Received", null=True, blank=True)
    stock_issue = models.CharField(max_length=250, verbose_name="Stock Issued", null=True, blank=True)
    purchases = models.CharField(max_length=250, verbose_name="purchases", null=True, blank=True)
    sales = models.CharField(max_length=250, verbose_name="sales", null=True, blank=True)
    csg = models.CharField(max_length=250, verbose_name="cost of goods sold", null=True, blank=True)
    opening_balance = models.CharField(max_length=250, verbose_name="opening balance", null=True, blank=True)
    closing_balance = models.CharField(max_length=250, verbose_name="closing balance", null=True, blank=True)

    def __str__(self):
        return self.location.registered_name or '-'

    class Meta:
        verbose_name = 'Chart of Account Settings'
        verbose_name_plural = 'Account Settings'
        indexes = [models.Index(fields=['id', 'location'])]



class ActivityLog(ExtraFields):
    user = models.ForeignKey("accounts.Users", on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    action_type = models.CharField(max_length=50, null=True, blank=True)
    module = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    objects = DefaultManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action_type} at {self.created_at}"



def xml_string(data):
    return """<cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID schemeID='""" + str(data.get('schemaType', '') or '') + """'>""" + str(
        data.get('schemaNo', '') or '') + """</cbc:ID>
            </cac:PartyIdentification>
            <cac:PostalAddress>
                <cbc:StreetName>""" + str(data.get('streetName') or '') + """</cbc:StreetName>
                <cbc:BuildingNumber>""" + str(data.get('buildingNumber') or '') + """</cbc:BuildingNumber>
                <cbc:PlotIdentification>""" + str(data.get('plotIdentification') or '') + """</cbc:PlotIdentification>
                <cbc:CitySubdivisionName>""" + str(data.get('citySubdivisionName') or '') + """</cbc:CitySubdivisionName>
                <cbc:CityName>""" + str(data.get('cityName') or '') + """</cbc:CityName>
                <cbc:PostalZone>""" + str(data.get('postalZone') or '') + """</cbc:PostalZone>
                <cac:Country>
                    <cbc:IdentificationCode>SA</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>""" + str(data.get('companyID') or '') + """</cbc:CompanyID>
                <cac:TaxScheme>
                    <cbc:ID>""" + str(data.get('taxID') or '') + """</cbc:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:PartyLegalEntity>
                <cbc:RegistrationName>""" + str(data.get('registrationName') or '') + """</cbc:RegistrationName>
            </cac:PartyLegalEntity>
        </cac:Party>
    </cac:AccountingSupplierParty>"""


# customer xml
def customer_xml(data):
    return """<cac:AccountingCustomerParty>
    <cac:Party>
        <cac:PostalAddress>
            <cbc:StreetName>""" + (data.get('streetName') or '') + """</cbc:StreetName>
            <cbc:BuildingNumber>""" + (data.get('buildingNumber') or '') + """</cbc:BuildingNumber>
            <cbc:CitySubdivisionName>""" + (data.get('citySubdivisionName') or '') + """</cbc:CitySubdivisionName>
            <cbc:CityName>""" + (data.get('cityName') or '') + """</cbc:CityName>
            <cbc:PostalZone>""" + (data.get('postalZone') or '') + """</cbc:PostalZone>
            <cac:Country>
                <cbc:IdentificationCode>SA</cbc:IdentificationCode>
            </cac:Country>
        </cac:PostalAddress>
        <cac:PartyTaxScheme>
            <cbc:CompanyID>""" + (data.get('companyID') or '') + """</cbc:CompanyID>
            <cac:TaxScheme>
                <cbc:ID>""" + (data.get('taxID') or '') + """</cbc:ID>
            </cac:TaxScheme>
        </cac:PartyTaxScheme>
        <cac:PartyLegalEntity>
            <cbc:RegistrationName>""" + (data.get('registrationName') or '') + """</cbc:RegistrationName>
        </cac:PartyLegalEntity>
    </cac:Party>
</cac:AccountingCustomerParty>"""


@receiver(post_save, sender=Suppliers, dispatch_uid="update_xml_text")
def update_xml_text_signal(sender, instance, created, **kwargs):
    xml_data = {
        'schemaType': instance.scheme_type, 'schemaNo': instance.scheme_no,
        'streetName': (instance.street_name or "صلاح الدين | Salah Al-Din"),
        'buildingNumber': (instance.building_number or "1111"),
        'plotIdentification': (instance.plot_identification or ""),
        'citySubdivisionName': (instance.city_subdivision_name or "المروج | Al-Murooj"),
        'cityName': (instance.city_name or "الرياض | Riyadh"),
        'postalZone': (instance.postal_zone or "12222"),
        'companyID': (instance.tax_id or "399999999800003"),
        'taxID': (instance.tax_scheme or "VAT"),
        'registrationName': (instance.registration_name or "شركة نماذج فاتورة المحدودة | Fatoora Samples LTD"),
    }

    xml_result = xml_string(xml_data)

    if created or instance.xml_data != xml_result:
        instance.xml_data = xml_result
        instance.save()


@receiver(post_save, sender=Customers, dispatch_uid="updated_xml_text")
def update_xml_text_signal(sender, instance, created, **kwargs):
    xml_data = {
        'streetName': (instance.street_name or "صلاح الدين | Salah Al-Din"),
        'buildingNumber': (instance.building_number or "1111"),
        'citySubdivisionName': (instance.city_subdivision_name or "المروج | Al-Murooj"),
        'cityName': (instance.city_name or "الرياض | Riyadh"),
        'postalZone': (instance.postal_zone or "12222"),
        'companyID': (instance.tax_id or "399999999800003"),
        'taxID': (instance.tax_scheme or "VAT"),
        'registrationName': (instance.registration_name or "شركة نماذج فاتورة المحدودة | Fatoora Samples LTD"),
    }

    xml_result = customer_xml(xml_data)

    if created or instance.xml_data != xml_result:
        instance.xml_data = xml_result
        instance.save()


@receiver(post_save, sender=MediaFiles, dispatch_uid="create_or_update_thumbnail")
def create_or_update_thumbnail(sender, instance, **kwargs):
    if instance.file_type == 'image' and instance.file:
        try:
            original_image = Image.open(instance.file)
            new_size = (200, 200)
            original_image.thumbnail(new_size)
            file_format = original_image.format or "JPEG"
            thumbnail_io = BytesIO()
            original_image.save(thumbnail_io, format=file_format)
            thumbnail_content = ContentFile(thumbnail_io.getvalue())
            instance.thumbnail.save(instance.file_name, thumbnail_content, save=False)

            instance.save(update_fields=["thumbnail"])
        except Exception as e:
            print(f"Thumbnail generation failed: {e}")


@receiver(post_save, sender=BusinessProfile, dispatch_uid="create_business_profile")
def create_business_profile_signal(sender, instance, created, **kwargs):
    try:
        if not created:
            return

        # InvoiceSettings.objects.create(business=instance)

        UnitOfMeasurement.objects.bulk_create([
            UnitOfMeasurement(location=instance, name="Unit", unit_value=1),
            UnitOfMeasurement(location=instance, name="Packet", unit_value=2),
            UnitOfMeasurement(location=instance, name="K.G", unit_value=3),
            UnitOfMeasurement(location=instance, name="Gram", unit_value=4),
            UnitOfMeasurement(location=instance, name="Dozen", unit_value=12),
        ])

        category = Categories.objects.create(name="General", location=instance)

        promo_code = PromoCodes.objects.create(location=instance, name="Discount", promo_type="%", value=0)

        TaxTypes.objects.bulk_create([
            TaxTypes(name="VAT", description="VAT", location=instance, default_status=True, tax_percent=15),
            TaxTypes(name="N/A", description="N/A", location=instance, default_status=True, tax_percent=0),
        ])

        tax_category = TaxTypes.objects.filter(name="VAT", location=instance).first()

        price_slots = SalePriceSlot.objects.create(location=instance, name="10 percent", unit_value=10, value_type="%")

        ProductItem.objects.create(location=instance, category=category, name="Default", promo=promo_code,
                                   cost_price_slot=1, price=1, tax_category=tax_category, item_type="sale",
                                   price_slot_id=price_slots.id)

        if not FinancialAccounts.objects.filter(location=instance).exists():
            create_financial_accounts(location=instance)

        customer = FinancialAccounts.objects.filter(location=instance, title="Accounts Receivable (A/R)").first()
        supplier = FinancialAccounts.objects.filter(location=instance, title="Accounts Payable (A/P)").first()
        opening_balance = FinancialAccounts.objects.filter(location=instance, title="Opening Balance").first()
        closing_balance = FinancialAccounts.objects.filter(location=instance, title="Closing Balance").first()

        customer_account = None
        supplier_account = None

        if customer:
            customer_account, _ = FinancialAccounts.objects.get_or_create(location=instance, title="Customer",
                                                                          code="CU-0000", parent=customer,
                                                                          defaults={"type": customer.type})

        if supplier:
            supplier_account, _ = FinancialAccounts.objects.get_or_create(location=instance, title="Supplier",
                                                                          code="SU-0000", parent=supplier,
                                                                          defaults={"type": supplier.type})

        cash_account = FinancialAccounts.objects.filter(location=instance, title="Cash").first()
        credit_account = FinancialAccounts.objects.filter(location=instance, title="Credit Card Payables").first()
        bank_account = FinancialAccounts.objects.filter(location=instance, code="BK-0000").first()
        tax = FinancialAccounts.objects.filter(location=instance, code="LI-0003").first()
        cgs = FinancialAccounts.objects.filter(location=instance, code="CG-0000").first()

        PaymentTypes.objects.bulk_create([
            PaymentTypes(name="Cash,نقدي", payment_code="10", location=instance, default_status=True,
                         chart_of_account=cash_account),
            PaymentTypes(name="Credit,ذمم", payment_code="30", location=instance, default_status=True,
                         chart_of_account=credit_account),
            PaymentTypes(name="Bank Transfer,حوالة بنكية", payment_code="42", location=instance,
                         default_status=True, chart_of_account=bank_account),
            PaymentTypes(name="Bank Card, Visa Mada", payment_code="48", location=instance, default_status=True,
                         chart_of_account=credit_account)
        ])

        if customer_account:
            Parties.objects.get_or_create(account_type="customer", location=instance, name="Default",
                                          chart_of_account=customer_account)

        if supplier_account:
            Parties.objects.get_or_create(account_type="supplier", location=instance, name="Vendor (Cash)",
                                          chart_of_account=supplier_account)

        setting, _ = AccountSetting.objects.get_or_create(location=instance)

        if bank_account:
            setting.banks = str(bank_account.id)

        if supplier:
            setting.payable_account = str(supplier.id)

        if opening_balance:
            setting.opening_balance = str(opening_balance.id)

        if closing_balance:
            setting.closing_balance = str(closing_balance.id)

        if cgs:
            setting.csg = str(cgs.id)

        if tax:
            setting.tax = str(tax.id)

        master_accounts = FinancialAccounts.objects.filter(location=instance, parent__isnull=True)
        for acc in master_accounts:
            if acc.title == "Equity":
                setting.equity = str(acc.id)
            elif acc.title == "Expense":
                setting.expense = str(acc.id)
            elif acc.title == "Revenue":
                setting.income = str(acc.id)

        financial_accounts = FinancialAccounts.objects.filter(location=instance, parent__isnull=False)

        account_map = {
            "Cash": "cash_account",
            "Petty Cash": "cash_account",
            "Accounts Receivable (A/R)": "receive_account",
            "Inventory": "inventory",
            "Investments": "other",
            "Accounts Payable (A/P)": "payable_account",
            "Credit Card Payables": "payable_account",
            "Loans Payable": "payable_account",
            "Taxes Payable": "tax",
            "Owner's Equity": "equity",
            "Payroll Liabilities": "profit_loss",
            "Retained Earnings": "stock_issue",
            "Common Stock": "stock_receive",
            "Sales Revenue": "sales",
            "Service Revenue": "sales",
            "Interest Income": "income",
            "Rental Income": "income",
            "Cost of Goods Sold (COGS)": "csg",
            "Rent Expense": "expense",
            "Salaries & Wages": "expense",
            "Utilities": "expense",
            "Office Supplies": "expense",
            "Bank Fees": "banks",
        }

        for acc in financial_accounts:
            field = account_map.get(acc.title)
            if field and not getattr(setting, field):
                setattr(setting, field, str(acc.id))

        setting.save()

    except Exception as e:
        logging.exception("Error during BusinessProfile signal")
