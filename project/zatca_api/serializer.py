import base64
import json

from rest_framework import serializers

from .csr.csid_create import generate_csid, generate_x509
from .models import BusinessLocation, Sandbox, Simulation, Production
from .task import generate_credentials_task

from django.forms.models import model_to_dict

from .zatca_operations.zatca import Zatca


class LocationSerializer(serializers.ModelSerializer):
    # sandbox = serializers.SerializerMethodField()
    # simulation = serializers.SerializerMethodField()
    # production = serializers.SerializerMethodField()
    business_name = serializers.CharField(source='seller_name', read_only=True)
    otp = serializers.CharField(write_only=True, required=False, max_length=6)
    x509 = serializers.CharField(write_only=True, required=False, max_length=6)

    # def get_sandbox(self, instance):
    #     return {
    #         "csr": bool(instance.sandbox.csr),
    #         "csid": bool(instance.sandbox.csid),
    #         "x509": bool(instance.sandbox.x509_certificate)
    #     }
    #
    # def get_simulation(self, instance):
    #     return {
    #         "csr": bool(instance.simulation.csr),
    #         "csid": bool(instance.simulation.csid),
    #         "x509": bool(instance.simulation.x509_certificate)
    #     }
    #
    # def get_production(self, instance):
    #     return {
    #         "csr": bool(instance.production.csr),
    #         "csid": bool(instance.production.csid),
    #         "x509": bool(instance.production.x509_certificate)
    #     }

    class Meta:
        model = BusinessLocation
        exclude = ['company', 'seller_name', 'tax_no', 'common_name', "schemeType", "schemeNo", "StreetName", "BuildingNumber", "PlotIdentification", "CitySubdivisionName", "CityName", "PostalZone"]
        extra_kwargs = {'authentication_token': {'read_only': True}}

    def update(self, instance, validated_data):



        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if validated_data['enable_zatca']:
            zatca = Zatca(instance.id)
            csr_response = zatca.generate_csr()
            if csr_response:
                Sandbox.objects.get_or_create(
                    location=instance,
                    defaults={
                        'csr': csr_response.get('csr'),
                        'private_key': csr_response.get('pvt'),
                        'public_key': csr_response.get('pbl'),
                        'csid': None,
                        'csid_base64': None,
                        'secret_csid': None,
                        'csid_request': None,
                        'x509_base64': None,
                        'x509_certificate': None,
                        'x509_secret': None,
                        'x509_request': None,
                    }
                )





        instance.save()
        return instance

    def create(self, validated_data):
        location = BusinessLocation.objects.create(**validated_data)
        if location.enable_zatca:
            zatca = Zatca(location.id)
            csr_response = zatca.generate_csr()

            if csr_response:
                Sandbox.objects.create(
                    location=location,
                    csr=csr_response.get('csr'),
                    private_key=csr_response.get('pvt'),
                    public_key=csr_response.get('pbl'),
                    csid=None, csid_base64=None, secret_csid=None, csid_request=None, x509_base64=None, x509_certificate=None, x509_secret=None, x509_request=None,
                )
            else:
                raise serializers.ValidationError("Failed to generate CSR for ZATCA.")
        return location


class BusinessLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessLocation
        fields = ["schemeType", "schemeNo", "StreetName", "BuildingNumber", "PlotIdentification", "CitySubdivisionName", "CityName", "PostalZone", "TaxScheme"]

class LocationListSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='seller_name', read_only=True)
    class Meta:
        model = BusinessLocation
        exclude = ['company', 'otp', 'seller_name', 'tax_no', 'common_name','authentication_token']

class CSIDSeliazer(serializers.Serializer):
    scope = serializers.CharField(max_length=250)
    otp = serializers.IntegerField()


class SandboxSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(max_length=6, required=True, write_only=True)

    class Meta:
        model = Sandbox
        fields = ['otp', 'csid']

    def update(self, instance, validated_data):
        result = generate_csid(instance.csr, validated_data['otp'], 'sandbox')
        if result.status_code != 200:
            raise serializers.ValidationError(result.text)
        result = json.loads(result.text)
        instance.csid = result['binarySecurityToken']
        instance.csid_base64 = base64.b64decode(bytes(result['binarySecurityToken'], 'utf-8')).decode('utf-8')
        instance.secret_csid = result['secret']
        instance.csid_request = result['requestID']
        instance.save()
        return instance


class SandboxX509Serializer(serializers.ModelSerializer):
    class Meta:
        model = Sandbox
        fields = ['x509_certificate']

    def update(self, instance, validated_data):
        result = generate_x509(instance.csid, instance.secret_csid, instance.csid_request, 'sandbox')
        if result.status_code != 200:
            raise serializers.ValidationError(result.text)
        result = json.loads(result.text)
        instance.x509_base64 = base64.b64decode(bytes(result['binarySecurityToken'], 'utf-8')).decode('utf-8')
        instance.x509_certificate = result['binarySecurityToken']
        instance.x509_secret = result['secret']
        instance.x509_request = result['requestID']
        instance.save()
        return instance


# --------------------------simualation------------------

class SimulationSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(max_length=6, required=True, write_only=True)

    class Meta:
        model = Simulation
        fields = ['otp']

    def update(self, instance, validated_data):
        result = generate_csid(instance.csr, validated_data['otp'], 'simulation')
        if result.status_code != 200:
            raise serializers.ValidationError(result.text)

        result = json.loads(result.text)
        instance.csid = result['binarySecurityToken']
        instance.csid_base64 = base64.b64decode(bytes(result['binarySecurityToken'], 'utf-8')).decode('utf-8')
        instance.secret_csid = result['secret']
        instance.csid_request = result['requestID']
        instance.save()
        return instance


class SimulationX509Serializer(serializers.ModelSerializer):
    class Meta:
        model = Simulation
        fields = ['x509_certificate']

    def update(self, instance, validated_data):
        result = generate_x509(instance.csid, instance.secret_csid, instance.csid_request, 'simulation')
        if result.status_code != 200:
            raise serializers.ValidationError(result.text)
        result = json.loads(result.text)
        instance.x509_base64 = base64.b64decode(bytes(result['binarySecurityToken'], 'utf-8')).decode('utf-8')
        instance.x509_certificate = result['binarySecurityToken']
        instance.x509_secret = result['secret']
        instance.x509_request = result['requestID']
        instance.save()
        return instance


# --------------------------simulation end--------------
class ProductionSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(max_length=6, required=True, write_only=True)

    class Meta:
        model = Production
        fields = ['otp']

    def update(self, instance, validated_data):
        result = generate_csid(instance.csr, validated_data['otp'], 'production')
        if result.status_code != 200:
            raise serializers.ValidationError(result.text)
        result = json.loads(result.text)
        instance.csid = result['binarySecurityToken']
        instance.csid_base64 = base64.b64decode(bytes(result['binarySecurityToken'], 'utf-8')).decode('utf-8')
        instance.secret_csid = result['secret']
        instance.csid_request = result['requestID']
        instance.save()
        return instance


class ProductionX509Serializer(serializers.ModelSerializer):
    otp = serializers.CharField(max_length=6, required=True, write_only=True)

    class Meta:
        model = Production
        fields = ['otp']

    def update(self, instance, validated_data):
        result = generate_x509(instance.csid, instance.secret_csid, instance.csid_request, 'production')
        if result.status_code != 200:
            raise serializers.ValidationError(result.text)
        result = json.loads(result.text)
        instance.x509_base64 = base64.b64decode(bytes(result['data']['binarySecurityToken'], 'utf-8')).decode('utf-8')
        instance.x509_certificate = result['binarySecurityToken']
        instance.x509_secret = result['secret']
        instance.x509_request = result['requestID']
        instance.save()
        return instance


class ComplainceSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(max_length=6, required=True, write_only=True)

    class Meta:
        model = Production
        fields = ['otp']

    def update(self, instance, validated_data):
        result = generate_x509(instance.csid, instance.secret_csid, instance.csid_request, 'production')
        if result.status_code != 200:
            raise serializers.ValidationError(result.text)
        result = json.loads(result.text)
        instance.x509_base64 = base64.b64encode(bytes(result['binarySecurityToken'], 'utf-8')).decode('utf-8')
        instance.x509_certificate = result['binarySecurityToken']
        instance.x509_secret = result['secret']
        instance.x509_request = result['requestID']
        instance.save()
        return instance
