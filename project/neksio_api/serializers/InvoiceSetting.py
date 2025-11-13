from rest_framework import serializers
from neksio_api.models import InvoiceSettings


class InvoiceSettingSerializer(serializers.ModelSerializer):
    thumbnail = serializers.FileField(source='logo.thumbnail', read_only=True)

    class Meta:
        model = InvoiceSettings
        exclude = ['created_at', 'updated_at', 'branch', 'policy_ar']
        extra_kwargs = {'business': {'write_only': True, 'required': False}, 'logo': {'write_only': True}}


class InvoiceLoadSerializer(serializers.ModelSerializer):
    thumbnail = serializers.FileField(source='logo.thumbnail', read_only=True)

    class Meta:
        model = InvoiceSettings
        exclude = ['created_at', 'updated_at', 'id', 'business', 'logo', 'default', 'branch']