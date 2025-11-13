from rest_framework import serializers
from django.db import transaction
from neksio_api.models import AssetLiabilityHead, AccountSetting, FinancialAccounts, IncomeExpenseHead
from utilities.code_generator import generate_financial_code
from .FinancialAccounts import FinancialAccountSerializer


class AssestLiabilityHeadSerializer(serializers.ModelSerializer):
    chart_of_account = FinancialAccountSerializer(read_only=True, required=False)

    class Meta:
        model = AssetLiabilityHead
        exclude = ['updated_at', 'created_at', 'location', 'deleted', 'id']

    def create(self, validated_data):

        if validated_data['type'] == 'asset':
            asset_type = 'Asset'
        else:
            asset_type = 'Liability'

        user = self.context['request'].user
        location = user.business_profile
        with transaction.atomic():
            serial_code = generate_financial_code(location, prefix='AL', bank_model=AssetLiabilityHead)

            account_setting = AccountSetting.objects.filter(location=location).first()

            parent_account = FinancialAccounts.objects.filter(id=account_setting.payable_account).first()

            financial_account = FinancialAccounts.objects.create(location=location, parent=parent_account,
                                                                 code=serial_code,
                                                                 type=asset_type,
                                                                 title=validated_data['name'],
                                                                 sub_ledger_type="Income Expense Head",
                                                                 is_sub_ledger_control=True)

            asset_head = AssetLiabilityHead.objects.create(chart_of_account=financial_account, **validated_data)
            return asset_head

    def update(self, instance, validated_data):
        with transaction.atomic():
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            if 'name' in validated_data:
                instance.chart_of_account.title = validated_data['name']
                instance.chart_of_account.save()

        return instance



class LiabilityFlatAccountSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="chart_of_account.id", read_only=True)
    title = serializers.CharField(source="chart_of_account.title", read_only=True)

    class Meta:
        model = AssetLiabilityHead
        fields = ["id", "title"]


class IncomeExpenseHeadSerializer(serializers.ModelSerializer):
    chart_of_account = FinancialAccountSerializer(read_only=True, required=False)

    class Meta:
        model = IncomeExpenseHead
        exclude = ['updated_at', 'created_at', 'location', 'deleted', 'id']

    def create(self, validated_data):
        if validated_data['type'] == 'expense':
            income_type = 'Expense'
        else:
            income_type = 'Revenue'

        user = self.context['request'].user
        location = user.business_profile
        with transaction.atomic():
            serial_code = generate_financial_code(location, prefix='IE', bank_model=IncomeExpenseHead)

            account_setting = AccountSetting.objects.filter(location=location).first()

            if validated_data['type'] == 'income':
                parent_account = FinancialAccounts.objects.filter(id=account_setting.income).first()
            else:
                parent_account = FinancialAccounts.objects.filter(id=account_setting.expense).first()

            financial_account = FinancialAccounts.objects.create(location=location, parent=parent_account,
                                                                 code=serial_code,
                                                                 type=income_type,
                                                                 title=validated_data['name'],
                                                                 sub_ledger_type="Income Expense Head",
                                                                 is_sub_ledger_control=True)

            income_expense = IncomeExpenseHead.objects.create(chart_of_account=financial_account, **validated_data)
            return income_expense

    def update(self, instance, validated_data):
        with transaction.atomic():
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            if 'name' in validated_data:
                instance.chart_of_account.title = validated_data['name']
                instance.chart_of_account.save()

        return instance