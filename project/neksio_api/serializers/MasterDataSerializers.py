import base64
import secrets
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers
from neksio_api.models import DummyData, BusinessTypes, Countries, TaxTypes, PaymentTypes, PaymentsHistory, \
    BusinessPackages, MediaFiles, EmailSupport, ActivityLog, AccountSetting
from utilities.modelMixins import send_notification_email


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            # base64 encoded image - decode
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            id = uuid.uuid4()
            data = ContentFile(base64.b64decode(imgstr), name ='einvotca'+ id.urn[9:] + '.' + ext)
            return super(Base64ImageField, self).to_internal_value(data)
        else:
            return super(Base64ImageField, self).to_internal_value(data)




class RecursiveFields(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class MediaFilesBase64Serializer(serializers.ModelSerializer):
    file = Base64ImageField()
    class Meta:
        model = MediaFiles
        fields = ['id', 'file']



class MediaFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFiles
        exclude = ['location', 'updated_at']
        extra_kwargs = {'thumbnail': {'read_only': True}, 'file': {'write_only': True}}


class MediaFilesDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFiles
        exclude = ['location', 'updated_at']
        extra_kwargs = {'file': {'required': False}}


class DummyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DummyData
        fields = '__all__'


class BusinessTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessTypes
        exclude = ['parent']


class CountriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Countries
        exclude = ['disabled', 'created_at', 'updated_at']


class TaxTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxTypes
        exclude = ['created_at', 'updated_at', 'default_status']


class PaymentTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTypes
        exclude = ['created_at', 'updated_at', 'default_status']


class BusinessPaymentsSerializer(serializers.ModelSerializer):
    package = serializers.CharField(source='package_plan.package_name', read_only=True)
    username = serializers.CharField(source='paid_by.username', read_only=True)

    class Meta:
        model = PaymentsHistory
        exclude = ['updated_at', 'package_plan', 'business_profile', 'paid_by']


class BusinessPackagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessPackages
        exclude = ['default_package']



type_choices = {
    1: 'Sales',
    2: 'After Sales',
    3: 'Technical Support',
    4: 'Advanced Support',
    5: 'Bugs',
    6: 'Enhancement'
}


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSupport
        exclude = ['updated_at', 'status', 'created_by', 'resolved_by',
                   'is_external', 'id', 'slug', 'created_at']
        extra_kwargs = {'is_external': {'write_only': False}}

    def create(self, validated_data):
        subject = f"Einvotca {validated_data['email']}"
        message = validated_data['message']
        keys = validated_data['support_type']
        send_notification_email(subject,
                                f"Subject:{validated_data['subject']} \n Contact: {validated_data['phone']} \n Type:{type_choices[keys]}, \n Message:{message}")

        return EmailSupport.objects.create(**validated_data)





#
def generate_key():
    private_key = secrets.token_bytes(32)
    return private_key.hex()


class PaymentHistorySerializer(serializers.ModelSerializer):
    paid_by = serializers.CharField(source='paid_by.username', read_only=True)
    location = serializers.CharField(source='business_profile.registered_name', read_only=True)
    plan = serializers.CharField(source='package_plan.package_name', read_only=True)

    class Meta:
        model = PaymentsHistory
        fields = ['reference_no', 'amount', 'payment_status', 'orderID', 'payerID', 'paid_by', 'location', 'plan']


class AccountSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountSetting
        exclude = ['id', 'location', 'created_at', 'updated_at']








class ActivityLogsSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    location = serializers.CharField(source='location.registered_name', read_only=True)

    class Meta:
        model = ActivityLog
        exclude = ['updated_at', 'created_at', 'deleted', 'id', 'ip_address']