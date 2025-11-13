from decimal import Decimal
from rest_framework import serializers
from neksio_api.models import FinancialAccounts, Suppliers, Customers
from products.models import ProductItem
from transactions.models import JournalProductDetail, JournalLine, JournalDetail
from utilities.code_generator import generate_reverse_entry_code
from django.db import transaction

from neksio_api.models import AccountSetting


def reverse_number(num):
    return num * -1


def custom_positive_number(num):
    if num < 0:
        return num * -1
    return num


from django.db.models import Sum


class PaymentEntriesSerializer(serializers.ModelSerializer):
    from_account = serializers.CharField(write_only=True)
    to_account = serializers.CharField(write_only=True)
    attachment = serializers.FileField(source='media_file.file', read_only=True)

    class Meta:
        model = JournalLine
        exclude = ['deleted', 'location', 'transaction_status', 'transaction_type', 'line_extension_amount',
                   'refund_reference', 'refunded', 'pending_amount', 'returned_amount', 'prepaid_amount',
                   'tax_inclusive_amount', 'tax_exclusive_amount', 'created_by', 'ref_no', 'data_collection']

    def create(self, validated_data):

        journal_lines = JournalLine.objects.filter(location=validated_data.get('location'),
                                                   invoice_no=validated_data.get('invoice_no'),
                                                   transaction_type="PAYMENT_VOUCHER").first()
        if journal_lines:
            raise serializers.ValidationError('Invoice number already exists for this location.')
        with transaction.atomic():
            from_account = validated_data.pop('from_account')
            to_account = validated_data.pop('to_account')
            journal_line = JournalLine.objects.create(transaction_type="PAYMENT_VOUCHER", transaction_status="PENDING",
                                                      **validated_data)

            from_account = FinancialAccounts.objects.filter(id=from_account).first()

            supplier = Suppliers.objects.filter(id=to_account).first()

            if supplier and supplier.chart_of_account:
                to_account = supplier.chart_of_account
            else:
                to_account = FinancialAccounts.objects.filter(id=to_account).first()

            amount = journal_line.paid_amount

            JournalDetail.objects.bulk_create(

                [JournalDetail(location=validated_data['location'], transaction=journal_line,
                               account_id=from_account.id, amount=-abs(amount),
                               description=f"Payment from {from_account.title}"),

                 JournalDetail(location=validated_data['location'], transaction=journal_line, account_id=to_account.id,
                               amount=amount,
                               description=f"Received by {to_account.title}"),
                 ])

            return journal_line


class ReversePaymentReceiptVoucherSerializer(serializers.ModelSerializer):
    return_entry = serializers.CharField(required=False)

    class Meta:
        model = JournalLine
        exclude = [
            'deleted', 'location', 'id', 'transaction_status', 'transaction_type', 'line_extension_amount',
            'refund_reference', 'refunded', 'pending_amount', 'returned_amount', 'prepaid_amount',
            'tax_inclusive_amount', 'tax_exclusive_amount', 'created_by', 'ref_no', 'date_time', 'invoice_no'
        ]

    def create(self, validated_data):
        return_entry_id = validated_data.get("return_entry")
        location = validated_data.get("location")

        if JournalLine.objects.filter(
                location=location,
                id=return_entry_id,
                transaction_type__in=["PAYMENT_VOUCHER", "RECEIPT_VOUCHER", "JOURNAL_ENTRY"],
                is_return=True
        ).exists():
            raise serializers.ValidationError('This entry has already been reversed.')

        journal_line = JournalLine.objects.filter(id=return_entry_id).first()
        if not journal_line:
            raise serializers.ValidationError("Original entry not found.")

        invoice_prefix_map = {
            "PAYMENT_VOUCHER": "RPV",
            "RECEIPT_VOUCHER": "RRV",
            "JOURNAL_ENTRY": "RJE"
        }

        invoice_number = invoice_prefix_map.get(journal_line.transaction_type)

        journal_details = JournalDetail.objects.filter(transaction=journal_line)

        if not journal_details.exists():
            raise serializers.ValidationError("No journal details found to reverse.")

        reverse_type = f"REVERSE_{journal_line.transaction_type}"

        paid_amount = journal_line.paid_amount

        with transaction.atomic():
            code = generate_reverse_entry_code(location, prefix=invoice_number, model=JournalLine)
            reversed_line = JournalLine.objects.create(invoice_no=code, transaction_type=reverse_type,
                                                       transaction_status="PENDING",
                                                       paid_amount=paid_amount, location=journal_line.location,
                                                       date_time=journal_line.date_time,
                                                       description=f"Reversal of Journal #{journal_line.invoice_no}",
                                                       is_return=True)

            reverse_details = []
            for detail in journal_details:
                reverse_details.append(
                    JournalDetail(location=journal_line.location, transaction=reversed_line,
                                  account_id=detail.account_id, account_title=detail.account_title,
                                  amount=-detail.amount, description=f"Reversal of {detail.description or ''}")
                )

            JournalDetail.objects.bulk_create(reverse_details)

            journal_line.is_return = True
            journal_line.save()

            return reversed_line


class PaymentVoucherSerializer(serializers.ModelSerializer):
    account = serializers.CharField(source='account.title', read_only=True)

    class Meta:
        model = JournalDetail
        fields = ['slug', 'account', 'amount']


class PaymentVoucherDetailSerializer(serializers.ModelSerializer):
    journal_lines = PaymentVoucherSerializer(many=True, read_only=True)

    class Meta:
        model = JournalLine
        fields = ['slug', 'invoice_no', 'date_time', 'description', 'journal_lines']


class ReceiptVoucherSerializer(serializers.ModelSerializer):
    from_account = serializers.CharField(write_only=True)
    to_account = serializers.CharField(write_only=True)
    attachment = serializers.FileField(source='media_file.file', read_only=True)

    class Meta:
        model = JournalLine
        exclude = ['deleted', 'location', 'transaction_status', 'transaction_type', 'line_extension_amount',
                   'refund_reference', 'refunded', 'pending_amount', 'returned_amount', 'prepaid_amount',
                   'tax_inclusive_amount', 'tax_exclusive_amount', 'created_by', 'ref_no']

    def create(self, validated_data):

        journal_lines = JournalLine.objects.filter(location=validated_data.get('location'),
                                                   invoice_no=validated_data.get('invoice_no'),
                                                   transaction_type="RECEIPT_VOUCHER").first()
        if journal_lines:
            raise serializers.ValidationError('Invoice number already exists for this location.')

        with transaction.atomic():

            from_account = validated_data.pop('from_account')
            to_account = validated_data.pop('to_account')

            journal_line = JournalLine.objects.create(transaction_type="RECEIPT_VOUCHER", transaction_status="PENDING",
                                                      **validated_data)

            from_account = FinancialAccounts.objects.filter(id=from_account).first()

            supplier = Suppliers.objects.filter(id=to_account).first()

            if supplier and supplier.chart_of_account:
                to_account = supplier.chart_of_account
            else:
                to_account = FinancialAccounts.objects.filter(id=to_account).first()

            amount = journal_line.paid_amount

            JournalDetail.objects.bulk_create(

                [JournalDetail(location=validated_data['location'], transaction=journal_line,
                               account_id=from_account.id, amount=amount,
                               description=f"Payment from {from_account.title}"),

                 JournalDetail(location=validated_data['location'], transaction=journal_line, account_id=to_account.id,
                               amount=-abs(amount),
                               description=f"Received by {to_account.title}"),
                 ])

            return journal_line


class OutOfStockRefundSerializer(serializers.ModelSerializer):
    quantity = serializers.SerializerMethodField(read_only=True)

    def get_quantity(self, obj):
        journal_detail = JournalProductDetail.objects.filter(item_id=obj.id).aggregate(stock_qty=Sum('quantity'))[
                             'stock_qty'] or 0
        return journal_detail

    class Meta:
        model = ProductItem
        fields = ['slug', 'name', 'cost_price_slot', 'item_type', 'quantity']


class JournalDetailsSerializer(serializers.ModelSerializer):
    debit = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True)
    credit = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True)

    class Meta:
        model = JournalDetail
        exclude = ['deleted', 'location', 'updated_at', 'slug', 'transaction']


class GeneralEntrySerializer(serializers.ModelSerializer):
    journal_lines = JournalDetailsSerializer(many=True)
    type = serializers.CharField(source='transaction_type', read_only=True, allow_blank=True)
    total_amount = serializers.SerializerMethodField(read_only=True)

    def get_total_amount(self, obj):
        journal_line = JournalDetail.objects.filter(transaction=obj).aggregate(amount=Sum('amount'))['amount'] or 0
        return journal_line

    class Meta:
        model = JournalLine
        fields = ['id', 'slug', 'invoice_no', 'date_time', 'payment_method', 'paid_amount', 'discount',
                  'tax_amount', 'returned_amount', 'pending_amount', 'journal_lines', 'type', 'description',
                  'total_amount']

    def create(self, validated_data):
        journal_detail = validated_data.pop('journal_lines')

        location = validated_data.get('location')
        invoice_no = validated_data.get('invoice_no')

        if JournalLine.objects.filter(location=location, invoice_no=invoice_no).exists():
            raise serializers.ValidationError('Invoice number already exists for this location.')

        with transaction.atomic():
            journal_line = JournalLine.objects.create(transaction_status="PENDING", transaction_type="JOURNAL_ENTRY",
                                                      **validated_data)

            journal_details = []
            for detail in journal_detail:
                debit = Decimal(detail.pop('debit', 0) or 0)
                credit = Decimal(detail.pop('credit', 0) or 0)

                if debit:
                    amount = debit
                else:
                    amount = -abs(credit)

                journal_details.append(
                    JournalDetail(location=location, transaction=journal_line, account_title=detail['account'].title,
                                  amount=amount, **detail))

            JournalDetail.objects.bulk_create(journal_details)

        return journal_line


class PartyOpeningBalanceSerializer(serializers.ModelSerializer):
    # from_account = serializers.UUIDField(write_only=True)
    to_account = serializers.UUIDField(write_only=True)
    type = serializers.CharField(write_only=True)

    class Meta:
        model = JournalLine
        exclude = [
            'deleted', 'location', 'transaction_status', 'transaction_type', 'line_extension_amount',
            'refund_reference', 'refunded', 'pending_amount', 'returned_amount', 'prepaid_amount',
            'tax_inclusive_amount', 'tax_exclusive_amount', 'created_by', 'ref_no', 'data_collection'
        ]

    def create(self, validated_data):
        party_type = validated_data.pop('type').lower()
        to_account_id = validated_data.pop('to_account')

        if JournalLine.objects.filter(location=validated_data.get('location'),
                                      invoice_no=validated_data.get('invoice_no'),
                                      transaction_type="OPENING_BALANCE").exists():

            raise serializers.ValidationError("Invoice number already exists for this location.")

        account_setting = AccountSetting.objects.filter(location=validated_data.get('location')).first()
        from_account = FinancialAccounts.objects.filter(id=account_setting.opening_balance).first()
        if not from_account:
            raise serializers.ValidationError("Invalid from_account ID.")

        party_model = Suppliers if party_type == "supplier" else Customers
        party = party_model.objects.filter(id=to_account_id).first()
        if not party or not party.chart_of_account:
            raise serializers.ValidationError(f"Invalid or unlinked {party_type} account.")

        to_account = party.chart_of_account

        with transaction.atomic():
            journal_line = JournalLine.objects.create(transaction_type="OPENING_BALANCE",
                                                      transaction_status="COMPLETED", **validated_data)

            if party_type == "customer":
                dr_account, cr_account = to_account, from_account
                description = f"Opening balance receivable from {party.name}"
            else:
                dr_account, cr_account = from_account, to_account
                description = f"Opening balance payable to {party.name}"

            JournalDetail.objects.bulk_create([
                JournalDetail(location=validated_data.get('location'), transaction=journal_line, account=dr_account,
                              amount=abs(journal_line.paid_amount), description="Opening balance adjustment (Dr)"),
                JournalDetail(location=validated_data.get('location'), transaction=journal_line, account=cr_account,
                              amount=-abs(journal_line.paid_amount), description=description),
            ])

        return journal_line
