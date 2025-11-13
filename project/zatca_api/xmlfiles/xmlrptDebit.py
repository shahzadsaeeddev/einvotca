from base64 import b64encode
from django.conf import settings

from ..statics.statics import INVOICE_CODES


def debitNote(business,invoiceType,**data):
    
    
    
    xml="""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2">
<ext:UBLExtensions>
   
</ext:UBLExtensions>
    
    <cbc:ProfileID>"""+data['profileID']+"""</cbc:ProfileID>
    <cbc:ID>"""+data['id']+"""</cbc:ID>
    <cbc:UUID>"""+data['uuid']+"""</cbc:UUID>
    <cbc:IssueDate>"""+data['issueDate']+"""</cbc:IssueDate>
    <cbc:IssueTime>"""+data['issueTime']+"""</cbc:IssueTime>
        """ + INVOICE_CODES[business][invoiceType] + """
    <cbc:Note languageID="ar">ABC</cbc:Note>
    <cbc:DocumentCurrencyCode>SAR</cbc:DocumentCurrencyCode>
    <cbc:TaxCurrencyCode>SAR</cbc:TaxCurrencyCode>
    <cac:BillingReference>
        <cac:InvoiceDocumentReference>
            <cbc:ID>?Invoice Number:"""+data['billingReference']['invoiceNo']+""" ; Invoice Issue Date: 2021-02-10?</cbc:ID>
        </cac:InvoiceDocumentReference>
    </cac:BillingReference>
    <cac:AdditionalDocumentReference>
        <cbc:ID>"""+data['additionalDocumentReference']['id']+"""</cbc:ID>
        <cbc:UUID>"""+data['additionalDocumentReference']['uuid']+"""</cbc:UUID>
    </cac:AdditionalDocumentReference>
    <cac:AdditionalDocumentReference>
        <cbc:ID>PIH</cbc:ID>
        <cac:Attachment>
            <cbc:EmbeddedDocumentBinaryObject mimeCode="text/plain">NWZlY2ViNjZmZmM4NmYzOGQ5NTI3ODZjNmQ2OTZjNzljMmRiYzIzOWRkNGU5MWI0NjcyOWQ3M2EyN2ZiNTdlOQ==</cbc:EmbeddedDocumentBinaryObject>
        </cac:Attachment>
    </cac:AdditionalDocumentReference>
    
    <cac:AdditionalDocumentReference>
        <cbc:ID>QR</cbc:ID>
        <cac:Attachment>
            <cbc:EmbeddedDocumentBinaryObject mimeCode="text/plain">ARdBaG1lZCBNb2hhbWVkIEFMIEFobWFkeQIPMzAxMTIxOTcxNTAwMDAzAxQyMDIyLTAzLTEzVDE0OjQwOjQwWgQHMTEwOC45MAUFMTQ0LjkGLFFuVkVleFc0bld2NENhRTM5YS82NkpwL09YTy9ldkhROHBEbEc3d2VxLzQ9B2BNRVlDSVFDOUtlN3JVMEcrbHcxakJ0RFkxVW5HVktmSGgwUk9BZFJuNTU0cEVYTmJVQUloQVB6S2l3cFBTV0h5Q0svbjQwUUZ2bEFzR1dsUzZ0L2VSQWNmTUdXdWVZUE8IWDBWMBAGByqGSM49AgEGBSuBBAAKA0IABGGDDKDmhWAITDv7LXqLX2cmr6+qddUkpcLCvWs5rC2O29W/hS4ajAK4Qdnahym6MaijX75Cg3j4aao7ouYXJ9EJSDBGAiEA7mHT6yg85jtQGWp3M7tPT7Jk2+zsvVHGs3bU5Z7YE68CIQD60ebQamYjYvdebnFjNfx4X4dop7LsEBFCNSsLY0IFaQ==</cbc:EmbeddedDocumentBinaryObject>
        </cac:Attachment>
</cac:AdditionalDocumentReference><cac:Signature>
      <cbc:ID>urn:oasis:names:specification:ubl:signature:Invoice</cbc:ID>
      <cbc:SignatureMethod>urn:oasis:names:specification:ubl:dsig:enveloped:xades</cbc:SignatureMethod>
</cac:Signature><cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID schemeID="CRN">"""+data['accountingSupplierParty']['id']+"""</cbc:ID>
            </cac:PartyIdentification>
            <cac:PostalAddress>
                <cbc:StreetName>"""+data['accountingSupplierParty']['streetName']+"""</cbc:StreetName>
                <cbc:BuildingNumber>"""+data['accountingSupplierParty']['buildingNumber']+"""</cbc:BuildingNumber>
                <cbc:PlotIdentification>"""+data['accountingSupplierParty']['plotIdentification']+"""</cbc:PlotIdentification>
                <cbc:CitySubdivisionName>"""+data['accountingSupplierParty']['citySubdivisionName']+"""</cbc:CitySubdivisionName>
                <cbc:CityName>"""+data['accountingSupplierParty']['cityName']+"""</cbc:CityName>
                <cbc:PostalZone>"""+data['accountingSupplierParty']['postalZone']+"""</cbc:PostalZone>
                <cac:Country>
                    <cbc:IdentificationCode>SA</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>"""+data['accountingSupplierParty']['companyID']+"""</cbc:CompanyID>
                <cac:TaxScheme>
                    <cbc:ID>"""+data['accountingSupplierParty']['taxID']+"""</cbc:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:PartyLegalEntity>
                <cbc:RegistrationName>"""+data['accountingSupplierParty']['registrationName']+"""</cbc:RegistrationName>
            </cac:PartyLegalEntity>
        </cac:Party>
    </cac:AccountingSupplierParty>
    <cac:AccountingCustomerParty>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID schemeID="NAT">"""+data['accountingCustomerParty']['id']+"""</cbc:ID>
            </cac:PartyIdentification>
            <cac:PostalAddress>
                <cbc:StreetName>"""+data['accountingCustomerParty']['streetName']+"""</cbc:StreetName>
                <cbc:AdditionalStreetName>"""+data['accountingCustomerParty']['additionalStreetName']+"""</cbc:AdditionalStreetName>
                <cbc:BuildingNumber>"""+data['accountingCustomerParty']['buildingNumber']+"""</cbc:BuildingNumber>
                <cbc:PlotIdentification>"""+data['accountingCustomerParty']['plotIdentification']+"""</cbc:PlotIdentification>
                <cbc:CitySubdivisionName>"""+data['accountingCustomerParty']['citySubdivisionName']+"""</cbc:CitySubdivisionName>
                <cbc:CityName>"""+data['accountingCustomerParty']['cityName']+"""</cbc:CityName>
                <cbc:PostalZone>"""+data['accountingCustomerParty']['postalZone']+"""</cbc:PostalZone>
                <cac:Country>
                    <cbc:IdentificationCode>SA</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cac:TaxScheme>
                    <cbc:ID>"""+data['accountingCustomerParty']['taxID']+"""</cbc:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:PartyLegalEntity>
                <cbc:RegistrationName>"""+data['accountingCustomerParty']['registrationName']+"""</cbc:RegistrationName>
            </cac:PartyLegalEntity>
        </cac:Party>
    </cac:AccountingCustomerParty>
    <cac:Delivery>
        <cbc:ActualDeliveryDate>"""+data['actualDeliveryDate']+"""</cbc:ActualDeliveryDate>
        <cbc:LatestDeliveryDate>"""+data['actualDeliveryDate']+"""</cbc:LatestDeliveryDate>
    </cac:Delivery>
    <cac:PaymentMeans>
        <cbc:PaymentMeansCode>"""+data['paymentMeansCode']+"""</cbc:PaymentMeansCode>
        <cbc:InstructionNote>CANCELLATION_OR_TERMINATION</cbc:InstructionNote>
    </cac:PaymentMeans>
    <cac:AllowanceCharge>
        <cbc:ChargeIndicator>"""+data['allowanceCharge']['chargeIndicator']+"""</cbc:ChargeIndicator>
        <cbc:AllowanceChargeReason>"""+data['allowanceCharge']['allowanceChargeReason']+"""</cbc:AllowanceChargeReason>
        <cbc:Amount currencyID="SAR">"""+data['allowanceCharge']['amount']+"""</cbc:Amount>
        <cac:TaxCategory>
            <cbc:ID schemeAgencyID="6" schemeID="UN/ECE 5305">"""+data['allowanceCharge']['taxId']+"""</cbc:ID>
            <cbc:Percent>"""+data['allowanceCharge']['taxPercentage']+"""</cbc:Percent>
            <cac:TaxScheme>
                <cbc:ID schemeAgencyID="6" schemeID="UN/ECE 5153">"""+data['allowanceCharge']['taxScheme']+"""</cbc:ID>
            </cac:TaxScheme>
        </cac:TaxCategory>
    </cac:AllowanceCharge>
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="SAR">"""+data['taxTotal']['taxAmount']+"""</cbc:TaxAmount>
        <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="SAR">"""+data['taxTotal']['tsttaxableAmount']+"""</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="SAR">"""+data['taxTotal']['tsttaxAmount']+"""</cbc:TaxAmount>
            <cac:TaxCategory>
                <cbc:ID schemeAgencyID="6" schemeID="UN/ECE 5305">"""+data['taxTotal']['taxId']+"""</cbc:ID>
                <cbc:Percent>"""+data['taxTotal']['taxPercentage']+"""</cbc:Percent>
                <cac:TaxScheme>
                    <cbc:ID schemeAgencyID="6" schemeID="UN/ECE 5153">"""+data['taxTotal']['taxScheme']+"""</cbc:ID>
                </cac:TaxScheme>
            </cac:TaxCategory>
        </cac:TaxSubtotal>
    </cac:TaxTotal>
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="SAR">"""+data['taxAmount']+"""</cbc:TaxAmount>

    </cac:TaxTotal>
    <cac:LegalMonetaryTotal>
        <cbc:LineExtensionAmount currencyID="SAR">"""+data['legalMonetaryTotal']['lineExtensionAmount']+"""</cbc:LineExtensionAmount>
        <cbc:TaxExclusiveAmount currencyID="SAR">"""+data['legalMonetaryTotal']['taxExclusiveAmount']+"""</cbc:TaxExclusiveAmount>
        <cbc:TaxInclusiveAmount currencyID="SAR">"""+data['legalMonetaryTotal']['taxInclusiveAmount']+"""</cbc:TaxInclusiveAmount>
        <cbc:AllowanceTotalAmount currencyID="SAR">"""+data['legalMonetaryTotal']['allowanceTotalAmount']+"""</cbc:AllowanceTotalAmount>
        <cbc:PrepaidAmount currencyID="SAR">"""+data['legalMonetaryTotal']['prepaidAmount']+"""</cbc:PrepaidAmount>
        <cbc:PayableAmount currencyID="SAR">"""+data['legalMonetaryTotal']['payableAmount']+"""</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>"""
    for s in data['invoiceLines']:
        xml+="""<cac:InvoiceLine>
        <cbc:ID>1</cbc:ID>
        <cbc:InvoicedQuantity unitCode="PCE">"""+s['invoicedQuantity']+"""</cbc:InvoicedQuantity>
        <cbc:LineExtensionAmount currencyID="SAR">"""+s['lineExtensionAmount']+"""</cbc:LineExtensionAmount>
        <cac:TaxTotal>
            <cbc:TaxAmount currencyID="SAR">"""+s['taxAmount']+"""</cbc:TaxAmount>
            <cbc:RoundingAmount currencyID="SAR">"""+s['roundingAmount']+"""</cbc:RoundingAmount>

        </cac:TaxTotal>
        <cac:Item>
            <cbc:Name>"""+s['itemName']+"""</cbc:Name>
            <cac:ClassifiedTaxCategory>
                <cbc:ID>"""+s['taxId']+"""</cbc:ID>
                <cbc:Percent>"""+s['taxPercentage']+"""</cbc:Percent>
                <cac:TaxScheme>
                    <cbc:ID>"""+s['taxScheme']+"""</cbc:ID>
                </cac:TaxScheme>
            </cac:ClassifiedTaxCategory>
        </cac:Item>
        <cac:Price>
            <cbc:PriceAmount currencyID="SAR">"""+s['priceAmount']+"""</cbc:PriceAmount>
            <cac:AllowanceCharge>
                <cbc:ChargeIndicator>false</cbc:ChargeIndicator>
                <cbc:AllowanceChargeReason>"""+s['allowanceChargeReason']+"""</cbc:AllowanceChargeReason>
                <cbc:Amount currencyID="SAR">"""+s['allowanceChargeAmount']+"""</cbc:Amount>
            </cac:AllowanceCharge>
        </cac:Price>
    </cac:InvoiceLine>"""
    xml+="""</Invoice>"""

    return b64encode(bytes(xml,'utf-8')).decode('utf-8')