from rest_framework import serializers

from neksio_api.models import Customers
from transactions.models import JournalProductDetail, JournalLine
from transactions.serializers.SerializerMixins import InvoiceSetupMixin, QrCodeMixin


class SaleCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = ['slug', 'name']

class TransactionDetailSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source='item.item_name', read_only=True)

    class Meta:
        model = JournalProductDetail
        exclude = ['location', 'deleted', 'created_at', 'updated_at', 'invoice', 'id']


class TransactionsGeneralViewSerializer(QrCodeMixin, InvoiceSetupMixin, serializers.ModelSerializer):
    items_transactions = TransactionDetailSerializer(many=True)
    payment_method = serializers.CharField(source='payment_method.name', read_only=True)
    party = serializers.CharField(source='party.name', read_only=True)
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    zatca_status = serializers.CharField(source='zatca_transactions.invoice_status', read_only=True)
    qrcode = serializers.SerializerMethodField()
    invoice_setup = serializers.SerializerMethodField()


    class Meta:
        model = JournalLine
        exclude = ['location', 'refund_reference', 'deleted', 'updated_at', 'description', 'id',
                   'ref_no', 'data_collection', 'media_file']



class JournalLineSerializer(QrCodeMixin, serializers.ModelSerializer):
    items_transactions = TransactionDetailSerializer(many=True)
    payment_method = serializers.CharField(source='payment_method.name', read_only=True)
    party = SaleCustomerSerializer(read_only=True)
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    zatca_status = serializers.CharField(source='zatca_transactions.invoice_status', read_only=True)
    qrcode = serializers.SerializerMethodField()
    attachment = serializers.FileField(source='media_file.file', read_only=True)



    class Meta:
        model = JournalLine
        exclude = ['location', 'refund_reference', 'deleted', 'updated_at', 'description', 'id',
                   'ref_no', 'data_collection']