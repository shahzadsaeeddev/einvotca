from rest_framework import serializers
from neksio_api.models import FinancialAccounts
from neksio_api.serializers.FinancialAccounts import FinancialAccountsSerializer
from neksio_api.serializers.MasterDataSerializers import RecursiveFields
from transactions.models import JournalDetail, JournalLine
from transactions.serializers.SerializerMixins import BalanceSheetMixins, JournalDetailMixins, InventoryReportMixin, \
    SalePurchaseMixin


class TrialBalanceReportSerializer(serializers.ModelSerializer):
    account_code = serializers.CharField()
    account__title = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = JournalDetail
        fields = ['id', 'account__title', 'amount', 'account_code']


class IncomeStatementReportSerializer(serializers.ModelSerializer):
    account_code = serializers.CharField(source='charts')
    account_title = serializers.CharField(source='name')
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = JournalDetail
        fields = ['id', 'account_title', 'amount', 'account_code']


class SalePurchaseReportSerializer(SalePurchaseMixin, serializers.ModelSerializer):
    payment_method = serializers.CharField(source='payment_method.name', read_only=True)
    quantity = serializers.SerializerMethodField(read_only=True)
    item = serializers.SerializerMethodField(read_only=True)
    supplier = serializers.CharField(source='party.name', read_only=True)
    sale_price = serializers.SerializerMethodField(read_only=True)
    ime_no = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = JournalLine
        fields = ['id', 'payment_method', 'invoice_no', 'date_time', 'quantity', 'item', 'transaction_type',
                  'tax_amount', 'discount', 'paid_amount', 'pending_amount', 'supplier', 'payable_amount',
                  "cost_amount", "sale_price", 'ime_no']


class InventoryReportSerializer(InventoryReportMixin, serializers.ModelSerializer):
    payment_method = serializers.CharField(source='payment_method.name', read_only=True)
    quantity = serializers.SerializerMethodField(read_only=True)
    item = serializers.SerializerMethodField(read_only=True)
    balance = serializers.SerializerMethodField(read_only=True)
    supplier = serializers.CharField(source='party.name', read_only=True)
    ime_no = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = JournalLine
        fields = ['id', 'payment_method', 'invoice_no', 'date_time', 'quantity', 'item', 'transaction_type',
                  'tax_amount', 'discount', 'balance', 'supplier', 'payable_amount', 'ime_no']


class BalanceSheetTreeSerializer(BalanceSheetMixins, serializers.ModelSerializer):
    children = RecursiveFields(many=True, allow_null=True)
    balance = serializers.SerializerMethodField()
    account_title = serializers.CharField(source='title', read_only=True)

    class Meta:
        model = FinancialAccounts
        fields = [
            'id', 'code', 'account_title', 'created_at',
            'location', 'children', 'balance'
        ]


class JournalDetailViewSerializer(JournalDetailMixins, serializers.ModelSerializer):
    account = FinancialAccountsSerializer(many=False)
    invoice_no = serializers.CharField(source='transaction.invoice_no', read_only=True)
    balance = serializers.SerializerMethodField(read_only=True)
    attachment = serializers.FileField(source='transaction.media_file.file', read_only=True)

    class Meta:
        model = JournalDetail
        exclude = ['id', 'location', 'deleted']
