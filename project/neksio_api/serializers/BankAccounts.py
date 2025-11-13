from rest_framework import serializers
from django.db import transaction
from neksio_api.models import BankAccount, AccountSetting, FinancialAccounts
from transactions.models import JournalDetail
from .SerializersMixins import BankAccountMixins
from utilities.code_generator import generate_financial_code


class BankTransactionSerializer(serializers.ModelSerializer):
    transaction_type = serializers.CharField(source='transaction.transaction_type')
    date_time = serializers.DateTimeField(source='transaction.date_time')
    invoice_no = serializers.CharField(source='transaction.invoice_no')

    class Meta:
        model = JournalDetail
        fields = ['invoice_no', 'date_time', 'transaction_type', 'amount']


class BankAccountSerializer(BankAccountMixins, serializers.ModelSerializer):
    balance = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = BankAccount
        exclude = ['created_at', 'updated_at', 'location', 'deleted']

    def create(self, validated_data):
        user = self.context['request'].user
        location = user.business_profile

        with transaction.atomic():
            serial_code = generate_financial_code(location, prefix='BA', bank_model=BankAccount)

            account_setting = AccountSetting.objects.filter(location=location).first()
            parent_account = FinancialAccounts.objects.filter(id=account_setting.banks).first()
            financial_account = FinancialAccounts.objects.create(location=location, parent=parent_account,
                                                                 code=serial_code,
                                                                 type="Asset", title=validated_data['account_title'],
                                                                 sub_ledger_type="Bank Account",
                                                                 is_sub_ledger_control=True)

            bank_account = BankAccount.objects.create(chart_of_account=financial_account, **validated_data)
            return bank_account

    def update(self, instance, validated_data):
        with transaction.atomic():
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            if 'account_title' in validated_data:
                instance.chart_of_account.title = validated_data['account_title']
                instance.chart_of_account.save()

        return instance