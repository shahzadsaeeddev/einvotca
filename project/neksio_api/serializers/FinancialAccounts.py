from rest_framework import serializers
from neksio_api.models import FinancialAccounts
from .MasterDataSerializers import RecursiveFields
from .SerializersMixins import FinancialAccountMixins


class FinancialAccountListSerializer(FinancialAccountMixins, serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    class Meta:
        model = FinancialAccounts
        fields = ['id', 'title', 'code', 'balance']


class FinancialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialAccounts
        exclude = ['updated_at', 'created_at', 'location', 'deleted', 'id']


class FinancialAccountsSerializer(serializers.ModelSerializer):
    children = RecursiveFields(many=True, required=False, allow_null=True)

    class Meta:
        model = FinancialAccounts
        fields = ['slug', 'title', 'code', 'type', 'is_sub_ledger_control', 'sub_ledger_type', 'parent', 'children', ]

        extra_kwargs = {'children': {'read_only': True}}

    def create(self, validated_data):
        financial_accounts = FinancialAccounts.objects.filter(location=validated_data['location']).filter(
            code=validated_data['code'])

        if financial_accounts.exists():
            raise serializers.ValidationError('Charts of accounts code already exists')

        financial_account = FinancialAccounts.objects.create(**validated_data)
        return financial_account

    def update(self, instance, validated_data):
        validated_data.pop('children', None)
        financial_accounts = FinancialAccounts.objects.filter(location=instance.location).filter(
            code=validated_data['code']).exclude(id=instance.id)

        if financial_accounts.exists():
            raise serializers.ValidationError('Charts of accounts code already exists')

        FinancialAccounts.objects.filter(id=instance.id).update(**validated_data)

        return instance
