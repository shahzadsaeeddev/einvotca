from decimal import Decimal
from django.db.models.aggregates import Sum
from neksio_api.models import InvoiceSettings, FinancialAccounts
from .invoiceSetup import InvoiceSetupSerializer
from ..models import JournalDetail, JournalProductDetail
from ..qrcode import generate_qrcode


class QrCodeMixin:
    def get_qrcode(self, instance):
        return generate_qrcode(instance.location.registered_name, instance.location.tax_no,
                               str(instance.created_at.replace(tzinfo=None)), str(instance.payable_amount),
                               str(instance.tax_amount))


class InvoiceSetupMixin:

    def get_invoice_setup(self, instance):
        business = getattr(instance, 'business', None)

        if not business:
            request = self.context.get('request')
            if request and hasattr(request.user, 'business_profile'):
                business = request.user.business_profile

        if not business:
            return None

        invoice_settings = InvoiceSettings.objects.filter(business=business).order_by('-default', '-created_at').first()

        if not invoice_settings:
            return None

        return InvoiceSetupSerializer(invoice_settings).data


class BalanceSheetMixins:

    def get_balance(self, obj):
        if obj.children.exists():
            return ""

        journal_item = JournalDetail.objects.filter(account=obj).aggregate(
            amount=Sum('amount')
        )

        balance = journal_item['amount'] or 0

        if obj.code == 'EQ-0006':
            try:
                account = FinancialAccounts.objects.get(code='IN-0000', location=obj.location)

                total_income = JournalDetail.objects.filter(account__parent=account).aggregate(
                    total=Sum('amount')
                )['total'] or 0

                cogs_account = FinancialAccounts.objects.get(code='CG-0000', location=obj.location)
                cogs = JournalDetail.objects.filter(account=cogs_account).aggregate(amount=Sum('amount'))['amount'] or 0

                exp_account = FinancialAccounts.objects.get(code='EX-0000', location=obj.location)
                expense = JournalDetail.objects.filter(account__parent=exp_account).aggregate(amount=Sum('amount'))[
                              'amount'] or 0
                balance = total_income + cogs + expense



            except FinancialAccounts.DoesNotExist:
                cogs = Decimal('0.00')

        return str(balance)


class JournalDetailMixins:

    def get_balance(self, instance):
        first_entry = JournalDetail.objects.filter(account=instance.account,
                                                   transaction__location=instance.transaction.location).order_by(
            "transaction__date_time").first()

        if first_entry and first_entry.id == instance.id:
            return 0

        balance = \
            JournalDetail.objects.filter(account=instance.account, transaction__location=instance.transaction.location,
                                         transaction__date_time__lte=instance.transaction.date_time).aggregate(
                total=Sum('amount'))['total'] or 0

        return balance


class InventoryReportMixin:

    def get_balance(self, obj):
        balance = obj.journal_lines.aggregate(total=Sum('amount'))['total'] or 0
        return balance

    def get_quantity(self, obj):
        journal_detail = obj.items_transactions.first()
        return journal_detail.quantity if journal_detail and journal_detail.quantity else 0

    def get_item(self, obj):
        journal_line = obj.items_transactions.first()
        return journal_line.item.name if journal_line and journal_line.item else None

    def get_ime_no(self, obj):
        journal_line = obj.items_transactions.first()
        return journal_line.ime_number if journal_line and journal_line.ime_number else None


class SalePurchaseMixin:

    def get_quantity(self, obj):
        journal_detail = obj.items_transactions.first()
        return journal_detail.quantity if journal_detail and journal_detail.quantity else 0

    def get_item(self, obj):
        journal_line = obj.items_transactions.first()
        return journal_line.item.name if journal_line and journal_line.item else None

    def get_sale_price(self, obj):
        journal_detail = JournalProductDetail.objects.filter(invoice=obj.id).first()
        return journal_detail.rate if journal_detail and journal_detail.rate else 0

    def get_ime_no(self, obj):
        journal_line = obj.items_transactions.first()
        return journal_line.ime_number if journal_line and journal_line.ime_number else None
