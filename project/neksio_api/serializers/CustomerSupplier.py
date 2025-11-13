from rest_framework import serializers
from django.db import transaction
from neksio_api.models import Customers, AccountSetting, FinancialAccounts, Suppliers, Parties
from .SerializersMixins import PartiesBalanceMixins
from utilities.code_generator import generate_financial_code


class SupplierDetailsSerializer(PartiesBalanceMixins, serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()
    class Meta:
        model = Suppliers
        fields = ['id', 'name', 'phone', 'balance']


class CustomerSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parties
        fields = ['id', 'name']


class SuppliersSerializer(PartiesBalanceMixins, serializers.ModelSerializer):
    thumbnail = serializers.FileField(source='photo.thumbnail', read_only=True)
    balance = serializers.SerializerMethodField()


    class Meta:
        model = Suppliers
        exclude = ['location', 'deleted', 'xml_data', 'account_type', 'taxable']
        extra_kwargs = {'photo': {'write_only': True}}

    def create(self, validated_data):
        user = self.context['request'].user
        location = user.business_profile

        serial_code = generate_financial_code(location, prefix='SU', bank_model=Suppliers)

        account_setting = AccountSetting.objects.filter(location=location).first()
        parent_account = FinancialAccounts.objects.filter(id=account_setting.payable_account).first()

        financial_account = FinancialAccounts.objects.create(location=location, parent=parent_account,
                                                             code=serial_code,
                                                             type="Liability", title=validated_data['name'],
                                                             sub_ledger_type="Supplier",
                                                             is_sub_ledger_control=True)

        supplier = Suppliers.objects.create(chart_of_account=financial_account, **validated_data)
        return supplier

    def update(self, instance, validated_data):
        with transaction.atomic():
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            if 'name' in validated_data:
                instance.chart_of_account.title = validated_data['name']
                instance.chart_of_account.save()

        return instance


class CustomersSerializer(PartiesBalanceMixins, serializers.ModelSerializer):
    thumbnail = serializers.FileField(source='photo.thumbnail', read_only=True)
    balance = serializers.SerializerMethodField()


    class Meta:
        model = Customers
        exclude = ['location', 'deleted', 'xml_data', 'account_type']
        extra_kwargs = {'photo': {'write_only': True}}

    def create(self, validated_data):
        user = self.context['request'].user
        location = user.business_profile
        with transaction.atomic():
            serial_code = generate_financial_code(location, prefix='CU', bank_model=Customers)

            account_setting = AccountSetting.objects.filter(location=location).first()
            parent_account = FinancialAccounts.objects.filter(id=account_setting.receive_account).first()

            financial_account = FinancialAccounts.objects.create(location=location, parent=parent_account,
                                                                 code=serial_code,
                                                                 type="Liability", title=validated_data['name'],
                                                                 sub_ledger_type="Customer",
                                                                 is_sub_ledger_control=True)

            customer = Customers.objects.create(chart_of_account=financial_account, **validated_data)
            return customer

    def update(self, instance, validated_data):
        with transaction.atomic():
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()
            if 'name' in validated_data:
                instance.chart_of_account.title = validated_data['name']
                instance.chart_of_account.save()

        return instance
