from rest_framework import serializers
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from transactions.models import JournalLine, JournalProductDetail
from .ProductEntries import JournalProductDetailSerializer
from .SerializerMixins import InvoiceSetupMixin, QrCodeMixin
from ..transactions import Transaction


class JournalLinesPurchaseSerializer(QrCodeMixin, InvoiceSetupMixin, serializers.ModelSerializer):
    items_transactions = JournalProductDetailSerializer(many=True)
    cashier = serializers.CharField(source='created_by.first_name', read_only=True)
    qrcode = serializers.SerializerMethodField()
    customer = serializers.CharField(source='party.name', read_only=True)
    paid_via = serializers.CharField(source='payment_method.name', read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    invoice_setup = serializers.SerializerMethodField()


    class Meta:
        model = JournalLine
        exclude = ['location', 'deleted', 'ref_no', 'slug', 'updated_at',
                   'description', 'id', 'data_collection']
        extra_kwargs = {
            'party': {'write_only': True},
            'payment_method': {'write_only': True},
            'created_by': {'write_only': True},
            'ref_no': {'required': False},
            'invoice_no': {'required': False},
            'transaction_status': {'required': False}
        }

    def create(self, validated_data):
        items_transactions = validated_data.pop('items_transactions')

        journal_line = JournalLine.objects.filter(location=validated_data['location'],
                                                  invoice_no=validated_data['invoice_no'],
                                                  transaction_type="PURCHASE").first()

        if journal_line:
            raise ValidationError("Invoice number already exists for this Location.")

        with transaction.atomic():

            master = JournalLine.objects.create(**validated_data, transaction_type='PURCHASE',
                                                transaction_status='PENDING', )
            location = master.location.id

            total_tax_amount = 0
            total_payable_amount = 0
            total_discount_amount = 0

            for value in items_transactions:
                item = value['item']
                quantity = value['quantity']
                item_discount = value.get('discount', 0)
                item_rate = value.get('rate', 0)
                item_name = item.name

                rate = item_rate
                total = quantity * rate
                discount_amount = item_discount * quantity
                taxable_amount = total - discount_amount
                tax_percent = Decimal('0')
                if item.tax_category and hasattr(item.tax_category, 'tax_percent'):
                    tax_percent = Decimal(item.tax_category.tax_percent or 0)

                tax_amount = taxable_amount * (tax_percent / Decimal('100'))
                tax_inclusive_amount = taxable_amount + tax_amount
                JournalProductDetail.objects.create(invoice=master, total_inclusive_tax_amount=tax_inclusive_amount,
                                                    tax_amount=tax_amount, item_name=item_name, total=total,
                                                    location=validated_data['location'], cost=rate,
                                                    **value)

                total_tax_amount += tax_amount
                total_discount_amount += discount_amount
                total_payable_amount += tax_inclusive_amount

            master.payable_amount = total_payable_amount
            master.tax_amount = total_tax_amount
            master.discount = total_discount_amount
            master.save()

            methods = Transaction(location, master)
            methods.purchase()

        return master





class DebitNoteSerializer(QrCodeMixin, InvoiceSetupMixin, serializers.ModelSerializer):
    items_transactions = JournalProductDetailSerializer(many=True)
    cashier = serializers.CharField(source='created_by.first_name', read_only=True)
    qrcode = serializers.SerializerMethodField()
    supplier = serializers.CharField(source='party.name', read_only=True)
    paid_via = serializers.CharField(source='payment_method.name', read_only=True)
    invoice_setup = serializers.SerializerMethodField()
    return_invoice = serializers.CharField(required=False, allow_null=True)


    class Meta:
        model = JournalLine
        exclude = ['location', 'deleted', 'ref_no', 'slug', 'updated_at', 'description', 'id', 'transaction_status']
        extra_kwargs = {
            'party': {'write_only': True},
            'payment_method': {'write_only': True},
            'created_by': {'write_only': True},
            'ref_no': {'required': False},
            'invoice_no': {'required': False},
            'transaction_status': {'required': False}
        }

    def create(self, validated_data):
        items_transactions = validated_data.pop('items_transactions')
        return_inv = validated_data.pop('return_invoice', None)

        journal_line = JournalLine.objects.filter(location=validated_data['location'],
                                                  invoice_no=validated_data['invoice_no'],
                                                  transaction_type="DEBIT_NOTE").first()

        if journal_line:
            raise ValidationError("Invoice number already exists for this Location.")

        with transaction.atomic():
            master = JournalLine.objects.create(**validated_data, transaction_type='DEBIT_NOTE',
                                                transaction_status='PENDING')

            JournalLine.objects.filter(id=return_inv).update(is_return=True)

            location = master.location.id

            total_tax_amount = 0
            total_payable_amount = 0
            total_discount_amount = 0

            for value in items_transactions:
                item = value['item']
                quantity = value['quantity']
                item_discount = value.get('discount', 0)
                item_rate = value.get('rate', 0)
                item_name = item.name

                rate = item_rate
                cost_price = item.cost_price_slot
                total = quantity * rate
                discount_amount = item_discount * quantity
                taxable_amount = total - discount_amount
                tax_percent = Decimal('0')
                if item.tax_category and hasattr(item.tax_category, 'tax_percent'):
                    tax_percent = Decimal(item.tax_category.tax_percent or 0)

                tax_amount = taxable_amount * (tax_percent / Decimal('100'))
                tax_inclusive_amount = taxable_amount + tax_amount

                product_quantity = -abs(quantity)
                value.pop('quantity')
                JournalProductDetail.objects.create(invoice=master, total_inclusive_tax_amount=tax_inclusive_amount,
                                                    tax_amount=tax_amount, total=total,
                                                    location=validated_data['location'], item_name=item_name,
                                                    cost=cost_price,
                                                    quantity=product_quantity,  **value)

                total_tax_amount += tax_amount
                total_discount_amount += discount_amount
                total_payable_amount += tax_inclusive_amount

            master.payable_amount = -total_payable_amount
            master.tax_amount = -total_tax_amount
            master.discount = -total_discount_amount
            master.save()

            methods = Transaction(location, master)
            methods.debit_note()

        return master