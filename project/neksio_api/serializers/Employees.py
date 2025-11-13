from rest_framework import serializers
from django.db import transaction
from neksio_api.models import Employees, AccountSetting, FinancialAccounts
from .FinancialAccounts import FinancialAccountSerializer
from utilities.code_generator import generate_financial_code


class EmployeesSerializer(serializers.ModelSerializer):
    chart_of_account = FinancialAccountSerializer(read_only=True, required=False)

    class Meta:
        model = Employees
        exclude = ['updated_at', 'created_at', 'location', 'deleted', 'id']

    def create(self, validated_data):
        user = self.context['request'].user
        location = user.business_profile

        with transaction.atomic():
            serial_code = generate_financial_code(location, prefix='EM', bank_model=Employees)
            account_setting = AccountSetting.objects.filter(location=location).first()
            parent_account = FinancialAccounts.objects.filter(id=account_setting.expense).first()

            financial_account = FinancialAccounts.objects.create(location=location, parent=parent_account,
                                                                 title=validated_data['name'], code=serial_code,
                                                                 type="Expense", sub_ledger_type="Employee",
                                                                 is_sub_ledger_control=True)

            employee = Employees.objects.create(chart_of_account=financial_account, **validated_data)
            return employee

    def update(self, instance, validated_data):
        with transaction.atomic():
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            if 'name' in validated_data:
                instance.chart_of_account.title = validated_data['name']
                instance.chart_of_account.save()

        return instance