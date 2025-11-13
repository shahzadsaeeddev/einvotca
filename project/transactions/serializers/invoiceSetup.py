from rest_framework import serializers

from neksio_api.models import InvoiceSettings


class InvoiceSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceSettings
        fields = ['id', 'name', 'address', 'phone', 'tax_no', 'policy', 'default']