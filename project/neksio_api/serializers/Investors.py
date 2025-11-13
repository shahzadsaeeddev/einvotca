from rest_framework import serializers
from utilities.code_generator import generate_financial_code
from .FinancialAccounts import FinancialAccountSerializer
from ..models import Investor, AccountSetting, FinancialAccounts
from django.db import transaction


class InvestorSerializer(serializers.ModelSerializer):
    chart_of_account = FinancialAccountSerializer(read_only=True, required=False)

    class Meta:
        model = Investor
        fields = ['slug', 'is_default', 'equity_percentage', 'chart_of_account', 'title']

    def create(self, validated_data):
        user = self.context['request'].user
        location = user.business_profile

        with transaction.atomic():
            serial_code = generate_financial_code(location, prefix='IN', bank_model=Investor)

            account_setting = AccountSetting.objects.filter(location=location).first()

            parent_account = FinancialAccounts.objects.filter(id=account_setting.equity).first()

            financial_account = FinancialAccounts.objects.create(location=location, parent=parent_account,
                                                                 code=serial_code,
                                                                 type="Equity",
                                                                 title=validated_data['title'],
                                                                 sub_ledger_type="Investor", is_sub_ledger_control=True)

            investor = Investor.objects.create(chart_of_account=financial_account, **validated_data)
            return investor

    def update(self, instance, validated_data):
        with transaction.atomic():
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            if 'title' in validated_data:
                instance.chart_of_account.title = validated_data['title']
                instance.chart_of_account.save()

        return instance