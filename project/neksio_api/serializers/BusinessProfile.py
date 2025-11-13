import datetime
import re
import uuid

from rest_framework import serializers
from accounts.keycloak import update_role_self
from accounts.models import Users
from neksio_api.models import BusinessProfile, BusinessPackages, InvoiceSettings
from zatca_api.models import BusinessLocation


class CurrentPackagePlanSerializer(serializers.ModelSerializer):
    current_plan = serializers.CharField(source='package_plan.package_name', read_only=True)
    plan_price = serializers.CharField(source='package_plan.discount', read_only=True)

    class Meta:
        model = BusinessProfile
        fields = ['id', 'current_plan', 'expiry_date', 'plan_price']


class BusinessProfileSecretSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfile
        fields = ['authentication_secret']


class BusinessProfileSerializer(serializers.ModelSerializer):
    business_type_name = serializers.CharField(source='business_type.type_name', read_only=True)

    class Meta:
        model = BusinessProfile
        exclude = ['id', 'no_of_users', 'account_end_date', 'support_pin', 'no_of_locations']
        extra_kwargs = {'package_plan': {'read_only': True}}

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'META'):
            auth_token = request.META.get('HTTP_AUTHORIZATION')
            auth_token = auth_token.split(' ')[1]
        else:
            auth_token = None

        context = validated_data.pop('context')
        if self.context['request'].user.is_owner and not context.user.business_profile:
            now = datetime.datetime.now()
            package = BusinessPackages.objects.filter(default_package=True).first()

            new_data = BusinessProfile.objects.create(package_plan=package,
                                                      account_end_date=now + datetime.timedelta(days=30),
                                                      expiry_date=now + datetime.timedelta(days=30),
                                                      **validated_data)
            InvoiceSettings.objects.create(business=new_data, name=new_data.registered_name, phone=new_data.phone,
                                           address=new_data.registered_address, tax_no=new_data.tax_no,
                                           policy="Default Invoice Setup Policy")
            location = None
            name = new_data.registered_name
            identifier = new_data.id

            normalized_name = re.sub(r'[^a-z0-9]+', '_', name.strip().lower())
            normalized_name = normalized_name.strip('_')

            result = f"{normalized_name}_{identifier}"

            if new_data.country and new_data.country.short_name == "SA":
                location = BusinessLocation.objects.create(company=new_data,
                                                           seller_name=new_data.registered_name,
                                                           tax_no=validated_data['tax_no'],
                                                           common_name=new_data.registered_name,
                                                           registered_address=new_data.registered_name,
                                                           title='1100',
                                                           serial_number="1-einvotca |2- v1 |3-" + str(uuid.uuid4()))
            keyclaok_id, role_id = update_role_self(auth_token, self.context['request'].user.username, result,
                                                    new_data.business_type.name, new_data.country.short_name)
            Users.objects.filter(username=context.user).update(keycloak_uuid=keyclaok_id, collections=result,
                                                               business_profile=new_data,
                                                               is_owner=True, default_business_location=location)



        else:
            profile = BusinessProfile.objects.get(id=context.user.business_profile_id)
            for field, value in validated_data.items():
                setattr(profile, field, value)
            profile.save(update_fields=validated_data.keys())

            update_role_self(auth_token, self.context['request'].user.username,
                             self.context['request'].user.collections,
                             profile.business_type.name, profile.country.short_name)

        return validated_data
