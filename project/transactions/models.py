import datetime

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields.array import ArrayField
from django.db import models
from utilities.modelMixins import ExtraFields, DefaultFilterManager
from utilities.ChoiceFileds import TransactionChoices, TaxInvoiceChoices, TransactionStatusChoices
import uuid

User = get_user_model()


class JournalLine(ExtraFields):
    ref_no = models.CharField(max_length=50)
    invoice_no = models.CharField(max_length=40)
    date_time = models.DateTimeField()
    description = models.TextField(blank=True)
    created_by = models.ForeignKey('accounts.Users', on_delete=models.SET_NULL, null=True)
    transaction_type = models.CharField(max_length=25, blank=True, choices=TransactionChoices.choices)
    party = models.ForeignKey('neksio_api.Parties', on_delete=models.SET_NULL, null=True, related_name='parties')
    payment_method = models.ForeignKey('neksio_api.PaymentTypes', on_delete=models.SET_NULL, null=True,
                                       related_name='payment_method')
    media_file = models.ForeignKey('neksio_api.MediaFiles', on_delete=models.SET_NULL, related_name='media_files', null=True)
    line_extension_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_exclusive_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_inclusive_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    prepaid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    returned_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    transaction_status = models.CharField(max_length=15, choices=TransactionStatusChoices.choices)
    refunded = models.BooleanField(default=False)
    refund_reference = models.CharField(max_length=255, null=True, blank=True)
    qrcode = models.TextField(null=True, blank=True)
    is_return = models.BooleanField(default=False)
    payment_type = models.CharField(max_length=100, blank=True)
    carriage_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    carriage_source = models.CharField(max_length=255, null=True, blank=True)
    data_collection = models.JSONField(blank=True, null=True)
    is_sync = models.BooleanField(default=False)

    objects = DefaultFilterManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invoice_no']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['party']),
            models.Index(fields=['date_time']),
            models.Index(fields=['location']),
        ]

    def save(self, *args, **kwargs):
        if self._state.adding and not self.invoice_no:
            date_format = "SME%y%m%d%H%M%S"
            self.invoice_no = datetime.datetime.now().strftime(date_format)

        # Optional: auto-calculate pending_amount
        # self.pending_amount = self.payable_amount - self.paid_amount + self.returned_amount

        super().save(*args, **kwargs)

    def __str__(self):
        party_name = self.party.name if self.party else "N/A"
        return f"{self.invoice_no} | Customer: {party_name}"


class JournalProductDetail(ExtraFields):
    invoice = models.ForeignKey(JournalLine, on_delete=models.CASCADE, null=True, related_name='items_transactions')
    item = models.ForeignKey('products.ProductItem', on_delete=models.SET_NULL, null=True, related_name='history')
    ime_number = ArrayField(models.CharField(max_length=250), blank=True, default=list)
    item_name = models.CharField(max_length=120, null=True, blank=True)
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    total_inclusive_tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice.transaction_type} - {self.invoice.invoice_no}"


class JournalDetail(ExtraFields):
    transaction = models.ForeignKey(
        JournalLine,
        on_delete=models.CASCADE,
        related_name='journal_lines'
    )
    account = models.ForeignKey(
        'neksio_api.FinancialAccounts',
        on_delete=models.PROTECT, null=True, blank=True, related_name="journal_accounts"
    )
    account_title = models.CharField(max_length=120, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)

    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(fields=['transaction']),
            models.Index(fields=['account']),
        ]

    def __str__(self):
        return f"{self.account} | Amount: {self.amount}"


class DayClosing(ExtraFields):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='closing_transactions')
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    returns = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    objects = DefaultFilterManager()

    def __str__(self):
        return f"{self.user} | Closing Balance: {self.closing_balance}"

    class Meta:
        ordering = ['-created_at']


class DayClosingDetail(ExtraFields):
    day_closing = models.ForeignKey(DayClosing, on_delete=models.CASCADE, null=True, related_name='closing_detail')
    payment_type = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.payment_type} | Amount: {self.amount}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug', 'day_closing']),
        ]


class TaxTransactions(ExtraFields):
    invoice = models.ForeignKey(JournalLine, on_delete=models.SET_NULL, null=True, related_name='zatca_transactions')
    uuid = models.UUIDField(default=uuid.uuid4)

    icv = models.IntegerField(auto_created=True, default=1)
    document_currency = models.CharField(max_length=5)
    tax_currency = models.CharField(max_length=5)
    previous_invoice_hash = models.CharField(max_length=250)
    qrcode = models.TextField(blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    latest_delivery_date = models.DateField(null=True, blank=True)
    instruction_note = models.TextField(max_length=50, blank=True, null=True)
    billing_reference = models.CharField(max_length=50, blank=True, null=True)
    invoice_type = models.CharField(max_length=25, choices=TaxInvoiceChoices.choices)
    invoice_status = models.CharField(max_length=25, choices=TaxInvoiceChoices.choices)
    response_message = models.TextField(max_length=500, blank=True, null=True)
    xml = models.TextField(blank=True)
    objects = DefaultFilterManager()

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self._state.adding:
            last_id = TaxTransactions.objects.all().aggregate(largest=models.Max('icv'))['largest']
            if last_id is not None:
                self.icv = last_id + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.icv)
