from rest_framework import serializers

from .models import ZatcaInvoicesProduction


class ZatcaSandboxInvoiceSerializer(serializers.ModelSerializer):

    createdBy=serializers.CharField(source='createdBy.username',read_only=True)
    class Meta:
        model = ZatcaInvoicesProduction
        exclude = ['invoiceBase64','invoiceQrcode','location','updated_at']


class ZatcaSandboxInvoiceDashboardSerializer(serializers.Serializer):

    total=serializers.CharField(read_only=True)
    class Meta:
        fields ='__all__'
