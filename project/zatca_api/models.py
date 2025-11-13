from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from neksio_api.models import BusinessProfile
from .csr.csr_generator import create_csr

import secrets

from neksio_api.models import FinancialAccounts, AccountSetting


# Create your models here.


class BusinessLocation(models.Model):
    schemaList = (
        ('TIN', 'TIN'), ('GCC', 'GCC'), ('IQA', 'IQA'), ('PAS', 'PAS'), ('CRN', 'CRN'), ('MOM', 'MOM'), ('MLS', 'MLS'),
        ('700', '700'), ('SAG', 'SAG'), ('OTH', 'OTH'))
    company = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, blank=True, related_name="location")
    authentication_token = models.TextField(blank=True, max_length=2500)
    seller_name = models.CharField(blank=True, max_length=230)
    tax_no = models.CharField(blank=True, max_length=16)
    common_name = models.CharField(blank=True, max_length=230)
    organisation = models.CharField(blank=True, max_length=230)
    organisation_unit = models.CharField(blank=True, max_length=230)
    serial_number = models.CharField(blank=True, max_length=230)
    title = models.CharField(blank=True, max_length=230)
    registered_address = models.CharField(blank=True, max_length=230)
    business_category = models.CharField(blank=True, max_length=230)
    otp = models.CharField(blank=True, max_length=230)
    enable_zatca = models.BooleanField(blank=True, default=False)
    schemeType = models.CharField(max_length=50, verbose_name="Scheme ID", null=True, blank=True, choices=schemaList)
    schemeNo = models.BigIntegerField(verbose_name="Scheme Number", null=True, blank=True, )
    StreetName = models.CharField(max_length=255, verbose_name="Street Name", blank=True, null=True)
    BuildingNumber = models.CharField(max_length=50, verbose_name="Building Number", blank=True, null=True)
    PlotIdentification = models.CharField(max_length=50, verbose_name="Plot Identification", blank=True, null=True)
    CitySubdivisionName = models.CharField(max_length=255, verbose_name="City Subdivision Name", blank=True, null=True)
    CityName = models.CharField(max_length=255, verbose_name="City Name", blank=True, null=True)
    PostalZone = models.CharField(max_length=50, verbose_name="Postal Zone", blank=True, null=True)
    TaxScheme = models.CharField(max_length=50, verbose_name="Tax Type", blank=True, null=True)
    xml_text = models.TextField(verbose_name="XML Text", blank=True, null=True)

    def __str__(self):
        return self.common_name


class Sandbox(models.Model):
    location = models.OneToOneField(BusinessLocation, on_delete=models.CASCADE, blank=True,
                                    related_name="sandbox")
    private_key = models.TextField(blank=True, max_length=1000)
    public_key = models.TextField(blank=True, max_length=1000)
    csr = models.TextField(blank=True, max_length=2500)
    csid = models.TextField(blank=True, max_length=3500, null=True)
    csid_base64 = models.TextField(blank=True, max_length=3500, null=True)
    secret_csid = models.TextField(blank=True, max_length=2500, null=True)
    csid_request = models.TextField(blank=True, max_length=100, null=True)
    x509_base64 = models.TextField(blank=True, max_length=3500, null=True)
    x509_certificate = models.TextField(blank=True, max_length=3500, null=True)
    x509_secret = models.TextField(blank=True, max_length=500, null=True)
    x509_request = models.TextField(blank=True, max_length=100, null=True)

    def __str__(self):
        return self.location.common_name


class Simulation(models.Model):
    location = models.OneToOneField(BusinessLocation, blank=True, on_delete=models.CASCADE,
                                    related_name="simulation")
    private_key = models.TextField(blank=True, max_length=1000)
    public_key = models.TextField(blank=True, max_length=1000)
    csr = models.TextField(blank=True, max_length=2500)
    csid = models.TextField(blank=True, max_length=3500)
    csid_base64 = models.TextField(blank=True, max_length=3500)
    secret_csid = models.TextField(blank=True, max_length=2500)
    csid_request = models.TextField(blank=True, max_length=100)
    x509_base64 = models.TextField(blank=True, max_length=3500)
    x509_certificate = models.TextField(blank=True, max_length=3500)
    x509_secret = models.TextField(blank=True, max_length=500)
    x509_request = models.TextField(blank=True, max_length=100)

    def __str__(self):
        return self.location.common_name


class Production(models.Model):
    location = models.OneToOneField(BusinessLocation, on_delete=models.CASCADE, blank=True,
                                    related_name="production")
    private_key = models.TextField(blank=True, max_length=1000)
    public_key = models.TextField(blank=True, max_length=1000)
    csr = models.TextField(blank=True, max_length=2500)
    csid = models.TextField(blank=True, max_length=3500)
    csid_base64 = models.TextField(blank=True, max_length=3500)
    secret_csid = models.TextField(blank=True, max_length=2500)
    csid_request = models.TextField(blank=True, max_length=100)
    x509_base64 = models.TextField(blank=True, max_length=3500)
    x509_certificate = models.TextField(blank=True, max_length=3500)
    x509_secret = models.TextField(blank=True, max_length=500)
    x509_request = models.TextField(blank=True, max_length=100)

    def __str__(self):
        return self.location.common_name





def generate_key():
    private_key = secrets.token_bytes(32)
    return private_key.hex()


def xml_string(data):
    return """<cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID schemeID='""" + data.get('schemaType','') + """'>""" + str(data.get('schemaNo','')) + """</cbc:ID>
            </cac:PartyIdentification>
            <cac:PostalAddress>
                <cbc:StreetName>""" + (data.get('streetName') or '') + """</cbc:StreetName>
                <cbc:BuildingNumber>""" + (data.get('buildingNumber') or '') + """</cbc:BuildingNumber>
                <cbc:PlotIdentification>""" + (data.get('plotIdentification') or '') + """</cbc:PlotIdentification>
                <cbc:CitySubdivisionName>""" + (data.get('citySubdivisionName') or '') + """</cbc:CitySubdivisionName>
                <cbc:CityName>""" + data['cityName'] + """</cbc:CityName>
                <cbc:PostalZone>""" + (data.get('postalZone') or '') + """</cbc:PostalZone>
                <cac:Country>
                    <cbc:IdentificationCode>SA</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>""" + (data.get('companyID') or '') + """</cbc:CompanyID>
                <cac:TaxScheme>
                    <cbc:ID>""" + (data.get('taxID') or '') + """</cbc:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:PartyLegalEntity>
                <cbc:RegistrationName>""" + (data.get('registrationName') or '') + """</cbc:RegistrationName>
            </cac:PartyLegalEntity>
        </cac:Party>
    </cac:AccountingSupplierParty>"""

# @receiver(post_save, sender=BusinessLocation, dispatch_uid="update_xml_text")
# def update_xml_text_signal(sender, instance, created, **kwargs):
#     if not created and not getattr(instance, '_updating_xml', False):
#         instance._updating_xml = True
#
#         xml_data = {
#             'schemaType': instance.schemeType, 'schemaNo': instance.schemeNo, 'streetName': instance.StreetName, 'buildingNumber': instance.BuildingNumber, 'plotIdentification': instance.PlotIdentification,
#             'citySubdivisionName': instance.CitySubdivisionName, 'cityName': instance.CityName, 'postalZone': instance.PostalZone, 'companyID': instance.tax_no, 'taxID': instance.TaxScheme,
#             'registrationName': instance.seller_name,
#         }
#         xml_result = xml_string(xml_data)
#         instance.xml_text = xml_result
#         instance.save()





