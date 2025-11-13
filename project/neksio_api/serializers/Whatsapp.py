from rest_framework import serializers

from neksio_api.models import BusinessWhatsappProfile, WhatsappContacts


class BusinessWhatsappProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessWhatsappProfile
        exclude = ['id']
        read_only_fields = ['business_profile', 'collections']


class WhatsappIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessWhatsappProfile
        fields = ['phone_number']



class ContactImportSerializer(serializers.Serializer):
    file = serializers.FileField()



class WhatsAppContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsappContacts
        fields = ['id', 'number', 'name', 'city']

    def create(self, validated_data):
        user = self.context.get("user")

        return WhatsappContacts.objects.create(user=user, **validated_data)