from rest_framework import serializers
from transactions.models import JournalProductDetail

from ..models import JournalLine


class JournalProductDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = JournalProductDetail
        exclude = ['location', 'invoice', 'created_at', 'updated_at', 'id', 'deleted', 'slug']
        extra_kwargs = {
            'item': {'write_only': True},
            'tax_amount': {'required': False},
            'total': {'required': False},
        }


class JournalProductCreditNoteSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_id = serializers.CharField(source='item.id', read_only=True)

    class Meta:
        model = JournalProductDetail
        exclude = ['location', 'invoice', 'created_at', 'updated_at', 'id', 'deleted', 'slug']
        extra_kwargs = {
            'item': {'write_only': True},
            'tax_amount': {'required': False},
            'total': {'required': False},
        }


class journalCreditNoteInvoiceSerializer(serializers.ModelSerializer):
    items_transactions = JournalProductCreditNoteSerializer(many=True, read_only=True)

    class Meta:
        model = JournalLine
        fields = ['items_transactions', 'id', 'party', 'paid_amount', 'pending_amount', 'qrcode', 'tax_amount',
                  'tax_exclusive_amount', 'tax_inclusive_amount', 'discount', 'invoice_no']
