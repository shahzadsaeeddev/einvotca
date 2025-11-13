import base64
import json
import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from zatca_api.xmlfiles.slz_invoice import invoiceStep1, debitNote1, creditNote1
from .models import BusinessLocation, Sandbox, Simulation, Production

from .serializer import (LocationSerializer,
                         SandboxSerializer, SimulationSerializer,
                         ProductionSerializer, SandboxX509Serializer, SimulationX509Serializer,
                         ProductionX509Serializer, CSIDSeliazer, BusinessLocationSerializer)
from rest_framework import viewsets, permissions, generics, authentication, filters

from .sign_document.sign_service import sign_xml_document

from .xmlfiles.xmlrpt import invoices
from .xmlfiles.xmlrptCredit import creditNote
from .xmlfiles.xmlrptDebit import debitNote
from .zatca.clearance import ZatcaClearance
from .zatca.complience import ZatcaCompliance
from .zatca.reporting import ZatcaReporting
from invoices.models import ZatcaInvoicesProduction
from .task import generate_credentials_task

from .zatca_operations.zatca import Zatca
logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class LocationView(viewsets.ModelViewSet):
    queryset = BusinessLocation.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['registered_address', 'organisation', 'organisation_unit', 'authentication_token']

    def perform_create(self, serializer):
        return serializer.save(company=self.request.user.business_profile,
                               seller_name=self.request.user.business_profile.registered_name,
                               tax_no=self.request.user.business_profile.tax_no,
                               common_name=self.request.user.business_profile.registered_name)

    def get_queryset(self):
        return BusinessLocation.objects.filter(company=self.request.user.business_profile)


class OTPVerificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, location_id):
        try:
            location = BusinessLocation.objects.get(id=location_id)
        except BusinessLocation.DoesNotExist:
            return Response({"detail": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

        otp = request.data.get('otp')
        if not otp:
            return Response({"detail": "OTP is required"}, status=status.HTTP_400_BAD_REQUEST)

        zatca = Zatca(location.id)

        try:
            sandbox = Sandbox.objects.filter(location_id=location.id).first()
            if not sandbox:
                return Response({"detail": "Sandbox record not found"}, status=status.HTTP_404_NOT_FOUND)

            result_data = zatca.generate_csid(otp=otp, **sandbox.__dict__)
            if not result_data or result_data.status_code != 200:
                logger.error(f"CSID generation failed for location {location.id}")
                return Response({"detail": "Failed to generate CSID"}, status=status.HTTP_400_BAD_REQUEST)
            # zatca.generate_x509(**sandbox.__dict__)
            generate_credentials_task.delay(location.id, sandbox.id)

            return Response({"detail": "OTP validated, certificates generation successfully."},
                            status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error during CSID generation: {str(e)}")
            return Response({"detail": f"Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)




class LocationListView(generics.ListAPIView):
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    def get_queryset(self):
        return BusinessLocation.objects.filter(company=self.request.user.business_profile)


class BusinessLocationView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BusinessLocationSerializer
    lookup_field = 'id'

    def get_queryset(self):
        company = self.request.user.business_profile
        return BusinessLocation.objects.filter(company=company)


class GenerateCSID(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, location, *args, **kwargs):
        results = CSIDSeliazer().data
        return Response(results)

    def patch(self, request, location, *args, **kwargs):
        c = self.request.user.profile.location.filter(
            authentication_token=location).first()

        if c == None:
            return Response(
                {"status": "400", "Message": "Failed", "data": "account not found with current secret key"},
                status=400)
        if 'production' == request.data['scope']:
            slz = ProductionSerializer(c.production, data=request.data)
        elif 'simulation' == request.data['scope']:
            slz = SimulationSerializer(c.simulation, data=request.data)
        else:
            slz = SandboxSerializer(c.sandbox, data=request.data)
        if slz.is_valid():

            return Response(
                {"status": "200", "Message": "Success", "data": slz.data},
                status=200)
        else:
            return Response(
                {"status": "200", "Message": "Success", "data": slz.errors},
                status=400)


class SandboxCSIDView(generics.UpdateAPIView):
    queryset = Sandbox.objects.all()
    serializer_class = SandboxSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'location'

    def get_object(self, queryset=None):
        location = self.kwargs.get('location')
        obj = Sandbox.objects.get(location=location)
        return obj


class SandboxX509View(generics.UpdateAPIView):
    serializer_class = SandboxX509Serializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'location'

    def get_object(self, queryset=None):
        location = self.kwargs.get('location')
        obj = Sandbox.objects.get(location=location)
        return obj


class SimulationView(generics.RetrieveUpdateAPIView):
    queryset = Simulation.objects.all()
    serializer_class = SimulationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'location'

    def get_object(self, queryset=None):
        location = self.kwargs.get('location')
        obj = Simulation.objects.get(location=location)
        return obj


class SimulationX509View(generics.RetrieveUpdateAPIView):
    queryset = Simulation.objects.all()
    serializer_class = SimulationX509Serializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'location'

    def get_object(self, queryset=None):
        location = self.kwargs.get('location')
        obj = Simulation.objects.get(location=location)
        return obj


class ProductionView(generics.RetrieveUpdateAPIView):
    queryset = Production.objects.all()
    serializer_class = ProductionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'location'

    def get_object(self, queryset=None):
        location = self.kwargs.get('location')
        obj = Production.objects.get(location=location)
        return obj


class ProductionX509View(generics.RetrieveUpdateAPIView):
    queryset = Production.objects.all()
    serializer_class = ProductionX509Serializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'location'

    def get_object(self, queryset=None):
        location = self.kwargs.get('location')
        obj = Production.objects.get(location=location)
        return obj


class SandboxComplianceBase64(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):
        results = invoiceStep1().data
        return Response(results)

    def post(self, request, *args, **kwargs):
        try:
            c = self.request.user.profile.location.filter(
                authentication_token=self.request.META.get('HTTP_SECRET')).first()

            if c == None:
                return Response(
                    {"status": "400", "Message": "Fail", "data": "account not found with current secret key"},
                    status=400)
            signedInvoice = sign_xml_document(request.data['invoiceBase64'], c.sandbox.private_key,
                                              c.sandbox.csid_base64)
            invoice = {"invoiceHash": signedInvoice['invoiceHash'],
                       "uuid": request.data['uuid'], "invoice": signedInvoice['invoiceXml']}
            stats = ZatcaCompliance(c.sandbox.csid, c.sandbox.secret_csid, invoice, 'sandbox')
            return Response(
                {"status": "200", "Message": "Success", "qrcode": signedInvoice['invoiceQRCode'], "data": stats},
                status=200)

        except Exception as e:

            return Response({"status": "400", "Message": "Fail", "data": str(e)}, status=400)


# sandbox
class SandboxComplianceInvoice(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):
        results = invoiceStep1().data
        return Response(results)

    def post(self, request, *args, **kwargs):
        try:

            c = BusinessLocation.objects.filter(
                authentication_token=self.request.META.get('HTTP_SECRET')).first()

            if c == None:
                return Response(
                    {"status": "400", "Message": "Fail", "data": "account not found with current secret key"},
                    status=400)
            if 'invoice' == request.data['invoice']['documentType']:
                zlx = invoiceStep1(data=request.data)
                invoiceData = invoices(request.data['invoice']['invoiceType'], request.data['invoice']['documentType'],
                                       **request.data)
            elif 'debit_note' == request.data['invoice']['documentType']:
                zlx = debitNote1(data=request.data)
                invoiceData = debitNote(request.data['invoice']['invoiceType'], request.data['invoice']['documentType'],
                                        **request.data)
            else:
                zlx = creditNote1(data=request.data)
                invoiceData = creditNote(request.data['invoice']['invoiceType'],
                                         request.data['invoice']['documentType'], **request.data)
            if zlx.is_valid():
                signedInvoice = sign_xml_document(invoiceData, c.sandbox.private_key,
                                                  c.sandbox.csid_base64)
                invoice = {"invoiceHash": signedInvoice['invoiceHash'],
                           "uuid": request.data['uuid'], "invoice": signedInvoice['invoiceXml']}
                stats = ZatcaCompliance(c.sandbox.csid, c.sandbox.secret_csid, invoice, 'sandbox')
                ZatcaInvoicesProduction.objects.create(location=c,
                                                       invoiceNo=request.data['id'],
                                                       invoiceType=request.data['invoice']['invoiceType'],
                                                       documentType=request.data['invoice']['documentType'],
                                                       invoiceUuid=request.data['uuid'],
                                                       invoiceHash=signedInvoice['invoiceHash'],
                                                       invoiceBase64=signedInvoice['invoiceXml'],
                                                       invoiceQrcode=signedInvoice['invoiceQRCode'],
                                                       status="success",
                                                       status_code=200,
                                                       message=stats
                                                       , invoiceScope='sandbox',
                                                       compliance=True,
                                                       createdBy=self.request.user)
                return Response(
                    {"status": "200", "Message": "Success", "qrcode": signedInvoice['invoiceQRCode'],
                     "data": stats},
                    status=200)
            else:
                return Response({"status": "400", "Message": "Invalid Json Body Data", "data": zlx.errors},
                                status=400)
        except Exception as e:
            return Response({"status": "400", "Message": "Fail", "data": str(e)}, status=400)

    # sandbox


class SandboxReporting(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):

        results = invoiceStep1().data
        return Response(results)

    def post(self, request, *args, **kwargs):
        try:
            c = BusinessLocation.objects.filter(
                authentication_token=self.request.META.get('HTTP_SECRET')).first()

            if c == None:
                return Response({"status": "400", "Message": "Fail", "data": "Invalid Version Code"}, status=400)

            if 'invoice' == request.data['invoice']['documentType']:
                zlx = invoiceStep1(data=request.data)
                invoiceData = invoices(request.data['invoice']['invoiceType'],
                                       request.data['invoice']['documentType'], **request.data)
            elif 'debit_note' == request.data['invoice']['documentType']:
                zlx = debitNote1(data=request.data)
                invoiceData = debitNote(request.data['invoice']['invoiceType'],
                                        request.data['invoice']['documentType'], **request.data)
            else:
                zlx = creditNote1(data=request.data)
                invoiceData = creditNote(request.data['invoice']['invoiceType'],
                                         request.data['invoice']['documentType'], **request.data)
            if zlx.is_valid():
                signedInvoice = sign_xml_document(invoiceData, c.sandbox.private_key,
                                                  c.sandbox.x509_base64)
                invoice = {"invoiceHash": signedInvoice['invoiceHash'],
                           "uuid": request.data['uuid'], "invoice": signedInvoice['invoiceXml']}
                stats = ZatcaReporting(c.sandbox.x509_certificate, c.sandbox.x509_secret, invoice, "sandbox")
                ZatcaInvoicesProduction.objects.create(location=c,
                                                       invoiceNo=request.data['id'],
                                                       invoiceType=request.data['invoice']['invoiceType'],
                                                       documentType=request.data['invoice']['documentType'],
                                                       invoiceUuid=request.data['uuid'],
                                                       invoiceHash=signedInvoice['invoiceHash'],
                                                       invoiceBase64=signedInvoice['invoiceXml'],
                                                       invoiceQrcode=signedInvoice['invoiceQRCode'],
                                                       status="success",
                                                       status_code=200,
                                                       message=stats
                                                       , invoiceScope='sandbox',
                                                       compliance=False,
                                                       createdBy=self.request.user)
                return Response(
                    {"status": "200", "Message": "Success", "qrcode": signedInvoice['invoiceQRCode'],
                     "data": stats},
                    status=200)
            else:
                return Response({"status": "400", "Message": "Invalid Json Body Data", "data": zlx.error_messages},
                                status=400)
        except Exception as e:
            print(e)
            return Response({"status": "400", "Message": "Fail", "data": ""}, status=400)


class SandboxClearance(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):

        results = invoiceStep1().data
        return Response(results)

    def post(self, request, *args, **kwargs):
        try:
            c = BusinessLocation.objects.filter(
                authentication_token=self.request.META.get('HTTP_SECRET')).first()

            if c == None:
                return Response({"status": "400", "Message": "Fail", "data": "Invalid Version Code"}, status=400)

            if 'invoice' == request.data['invoice']['documentType']:
                zlx = invoiceStep1(data=request.data)
                invoiceData = invoices(request.data['invoice']['invoiceType'],
                                       request.data['invoice']['documentType'], **request.data)
            elif 'debit_note' == request.data['invoice']['documentType']:
                zlx = debitNote1(data=request.data)
                invoiceData = debitNote(request.data['invoice']['invoiceType'],
                                        request.data['invoice']['documentType'], **request.data)
            else:
                zlx = creditNote1(data=request.data)
                invoiceData = creditNote(request.data['invoice']['invoiceType'],
                                         request.data['invoice']['documentType'], **request.data)
            if zlx.is_valid():
                signedInvoice = sign_xml_document(invoiceData, c.sandbox.private_key,
                                                  c.sandbox.x509_base64)

                invoice = {"invoiceHash": signedInvoice['invoiceHash'],
                           "uuid": request.data['uuid'], "invoice": signedInvoice['invoiceXml']}
                stats = ZatcaClearance(c.sandbox.x509_certificate, c.sandbox.x509_secret, invoice, "sandbox")
                ZatcaInvoicesProduction.objects.create(location=c,
                                                       invoiceNo=request.data['id'],
                                                       invoiceType=request.data['invoice']['invoiceType'],
                                                       documentType=request.data['invoice']['documentType'],
                                                       invoiceUuid=request.data['uuid'],
                                                       invoiceHash=signedInvoice['invoiceHash'],
                                                       invoiceBase64=signedInvoice['invoiceXml'],
                                                       invoiceQrcode=signedInvoice['invoiceQRCode'],
                                                       status="success",
                                                       status_code=200,
                                                       message=stats
                                                       , invoiceScope='sandbox',
                                                       compliance=False,
                                                       createdBy=self.request.user)
                return Response(
                    {"status": "200", "Message": "Success", "qrcode": signedInvoice['invoiceQRCode'],
                     "data": stats},
                    status=200)
            else:
                return Response({"status": "400", "Message": "Invalid Json Body Data", "data": zlx.error_messages},
                                status=400)
        except Exception as e:
            print(e)
            return Response({"status": "400", "Message": "Fail", "data": ""}, status=400)


# simulation
class SimulationComplianceInvoice(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):
        results = invoiceStep1().data
        return Response(results)

    def post(self, request, *args, **kwargs):
        try:
            c = BusinessLocation.objects.filter(
                authentication_token=self.request.META.get('HTTP_SECRET')).first()

            if c == None:
                return Response(
                    {"status": "400", "Message": "Fail", "data": "account not found with current secret key"},
                    status=400)
            if 'invoice' == request.data['invoice']['documentType']:
                zlx = invoiceStep1(data=request.data)
                invoiceData = invoices(request.data['invoice']['invoiceType'], request.data['invoice']['documentType'],
                                       **request.data)
            elif 'debit_note' == request.data['invoice']['documentType']:
                zlx = debitNote1(data=request.data)
                invoiceData = debitNote(request.data['invoice']['invoiceType'], request.data['invoice']['documentType'],
                                        **request.data)
            else:
                zlx = creditNote1(data=request.data)
                invoiceData = creditNote(request.data['invoice']['invoiceType'],
                                         request.data['invoice']['documentType'], **request.data)
            if zlx.is_valid():
                signedInvoice = sign_xml_document(invoiceData, c.simulation.private_key,
                                                  c.simulation.csid_base64)
                invoice = {"invoiceHash": signedInvoice['invoiceHash'],
                           "uuid": request.data['uuid'], "invoice": signedInvoice['invoiceXml']}
                stats = ZatcaCompliance(c.simulation.csid, c.simulation.secret_csid, invoice, 'simulation')
                ZatcaInvoicesProduction.objects.create(location=c,
                                                       invoiceNo=request.data['id'],
                                                       invoiceType=request.data['invoice']['invoiceType'],
                                                       documentType=request.data['invoice']['documentType'],
                                                       invoiceUuid=request.data['uuid'],
                                                       invoiceHash=signedInvoice['invoiceHash'],
                                                       invoiceBase64=signedInvoice['invoiceXml'],
                                                       invoiceQrcode=signedInvoice['invoiceQRCode'],
                                                       status="success",
                                                       status_code=200,
                                                       message=stats
                                                       , invoiceScope='simulation',
                                                       compliance=True,
                                                       createdBy=self.request.user)
                return Response(
                    {"status": "200", "Message": "Success", "qrcode": signedInvoice['invoiceQRCode'],
                     "data": stats},
                    status=200)
            else:
                return Response({"status": "400", "Message": "Invalid Json Body Data", "data": zlx.errors},
                                status=400)
        except Exception as e:
            return Response({"status": "400", "Message": "Fail", "data": str(e)}, status=400)

    # sandbox


class SimulationReporting(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):

        results = invoiceStep1().data
        return Response(results)

    def post(self, request, *args, **kwargs):
        try:
            c = BusinessLocation.objects.filter(
                authentication_token=self.request.META.get('HTTP_SECRET')).first()

            if c == None:
                return Response({"status": "400", "Message": "Fail", "data": "Invalid Version Code"}, status=400)

            if 'invoice' == request.data['invoice']['documentType']:
                zlx = invoiceStep1(data=request.data)
                invoiceData = invoices(request.data['invoice']['invoiceType'],
                                       request.data['invoice']['documentType'], **request.data)
            elif 'debit_note' == request.data['invoice']['documentType']:
                zlx = debitNote1(data=request.data)
                invoiceData = debitNote(request.data['invoice']['invoiceType'],
                                        request.data['invoice']['documentType'], **request.data)
            else:
                zlx = creditNote1(data=request.data)
                invoiceData = creditNote(request.data['invoice']['invoiceType'],
                                         request.data['invoice']['documentType'], **request.data)
            if zlx.is_valid():
                signedInvoice = sign_xml_document(invoiceData, c.sandbox.private_key,
                                                  c.simulation.x509_base64)
                invoice = {"invoiceHash": signedInvoice['invoiceHash'],
                           "uuid": request.data['uuid'], "invoice": signedInvoice['invoiceXml']}
                stats = ZatcaReporting(c.simulation.x509_certificate, c.simulation.x509_secret, invoice, "simulation")
                ZatcaInvoicesProduction.objects.create(location=c,
                                                       invoiceNo=request.data['id'],
                                                       invoiceType=request.data['invoice']['invoiceType'],
                                                       documentType=request.data['invoice']['documentType'],
                                                       invoiceUuid=request.data['uuid'],
                                                       invoiceHash=signedInvoice['invoiceHash'],
                                                       invoiceBase64=signedInvoice['invoiceXml'],
                                                       invoiceQrcode=signedInvoice['invoiceQRCode'],
                                                       status="success",
                                                       status_code=200,
                                                       message=stats
                                                       , invoiceScope='simulation',
                                                       compliance=True,
                                                       createdBy=self.request.user)
                return Response(
                    {"status": "200", "Message": "Success", "qrcode": signedInvoice['invoiceQRCode'],
                     "data": stats},
                    status=200)
            else:
                return Response({"status": "400", "Message": "Invalid Json Body Data", "data": zlx.error_messages},
                                status=400)
        except Exception as e:
            print(e)
            return Response({"status": "400", "Message": "Fail", "data": ""}, status=400)


class SimulationClearance(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):

        results = invoiceStep1().data
        return Response(results)

    def post(self, request, *args, **kwargs):
        try:
            c = BusinessLocation.objects.filter(
                authentication_token=self.request.META.get('HTTP_SECRET')).first()

            if c == None:
                return Response({"status": "400", "Message": "Fail", "data": "Invalid Version Code"}, status=400)

            if 'invoice' == request.data['invoice']['documentType']:
                zlx = invoiceStep1(data=request.data)
                invoiceData = invoices(request.data['invoice']['invoiceType'],
                                       request.data['invoice']['documentType'], **request.data)
            elif 'debit_note' == request.data['invoice']['documentType']:
                zlx = debitNote1(data=request.data)
                invoiceData = debitNote(request.data['invoice']['invoiceType'],
                                        request.data['invoice']['documentType'], **request.data)
            else:
                zlx = creditNote1(data=request.data)
                invoiceData = creditNote(request.data['invoice']['invoiceType'],
                                         request.data['invoice']['documentType'], **request.data)
            if zlx.is_valid():
                signedInvoice = sign_xml_document(invoiceData, c.simulation.private_key,
                                                  c.simulation.x509_base64)

                invoice = {"invoiceHash": signedInvoice['invoiceHash'],
                           "uuid": request.data['uuid'], "invoice": signedInvoice['invoiceXml']}
                stats = ZatcaClearance(c.simulation.x509_certificate, c.simulation.x509_secret, invoice, "simulation")
                ZatcaInvoicesProduction.objects.create(location=c,
                                                       invoiceNo=request.data['id'],
                                                       invoiceType=request.data['invoice']['invoiceType'],
                                                       documentType=request.data['invoice']['documentType'],
                                                       invoiceUuid=request.data['uuid'],
                                                       invoiceHash=signedInvoice['invoiceHash'],
                                                       invoiceBase64=signedInvoice['invoiceXml'],
                                                       invoiceQrcode=signedInvoice['invoiceQRCode'],
                                                       status="success",
                                                       status_code=200,
                                                       message=stats
                                                       , invoiceScope='simulation',
                                                       compliance=True,
                                                       createdBy=self.request.user)
                return Response(
                    {"status": "200", "Message": "Success", "qrcode": signedInvoice['invoiceQRCode'],
                     "data": stats},
                    status=200)
            else:
                return Response({"status": "400", "Message": "Invalid Json Body Data", "data": zlx.error_messages},
                                status=400)
        except Exception as e:
            print(e)
            return Response({"status": "400", "Message": "Fail", "data": ""}, status=400)


# production

class ProductionComplianceInvoice(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):
        results = invoiceStep1().data
        return Response(results)

    def post(self, request, *args, **kwargs):
        try:
            c = BusinessLocation.objects.filter(
                authentication_token=self.request.META.get('HTTP_SECRET')).first()

            if c == None:
                return Response(
                    {"status": "400", "Message": "Fail", "data": "account not found with current secret key"},
                    status=400)
            if 'invoice' == request.data['invoice']['documentType']:
                zlx = invoiceStep1(data=request.data)
                invoiceData = invoices(request.data['invoice']['invoiceType'], request.data['invoice']['documentType'],
                                       **request.data)
            elif 'debit_note' == request.data['invoice']['documentType']:
                zlx = debitNote1(data=request.data)
                invoiceData = debitNote(request.data['invoice']['invoiceType'], request.data['invoice']['documentType'],
                                        **request.data)
            else:
                zlx = creditNote1(data=request.data)
                invoiceData = creditNote(request.data['invoice']['invoiceType'],
                                         request.data['invoice']['documentType'], **request.data)
            if zlx.is_valid():
                signedInvoice = sign_xml_document(invoiceData, c.production.private_key,
                                                  c.production.csid_base64)
                invoice = {"invoiceHash": signedInvoice['invoiceHash'],
                           "uuid": request.data['uuid'], "invoice": signedInvoice['invoiceXml']}
                stats = ZatcaCompliance(c.production.csid, c.production.secret_csid, invoice, 'production')
                return Response(
                    {"status": "200", "Message": "Success", "qrcode": signedInvoice['invoiceQRCode'],
                     "data": stats},
                    status=200)
            else:
                return Response({"status": "400", "Message": "Invalid Json Body Data", "data": zlx.errors},
                                status=400)
        except Exception as e:
            return Response({"status": "400", "Message": "Fail", "data": str(e)}, status=400)

    # sandbox


class ProductionReporting(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):

        results = invoiceStep1().data
        return Response(results)

    def post(self, request, *args, **kwargs):
        try:
            c = BusinessLocation.objects.filter(
                authentication_token=self.request.META.get('HTTP_SECRET')).first()

            if c == None:
                return Response({"status": "400", "Message": "Fail", "data": "Invalid Version Code"}, status=400)

            if 'invoice' == request.data['invoice']['documentType']:
                zlx = invoiceStep1(data=request.data)
                invoiceData = invoices(request.data['invoice']['invoiceType'],
                                       request.data['invoice']['documentType'], **request.data)
            elif 'debit_note' == request.data['invoice']['documentType']:
                zlx = debitNote1(data=request.data)
                invoiceData = debitNote(request.data['invoice']['invoiceType'],
                                        request.data['invoice']['documentType'], **request.data)
            else:
                zlx = creditNote1(data=request.data)
                invoiceData = creditNote(request.data['invoice']['invoiceType'],
                                         request.data['invoice']['documentType'], **request.data)
            if zlx.is_valid():
                signedInvoice = sign_xml_document(invoiceData, c.production.private_key,
                                                  c.production.x509_base64)
                invoice = {"invoiceHash": signedInvoice['invoiceHash'],
                           "uuid": request.data['uuid'], "invoice": signedInvoice['invoiceXml']}
                stats = ZatcaReporting(c.simulation.x509_certificate, c.simulation.x509_secret, invoice, "production")
                return Response(
                    {"status": "200", "Message": "Success", "qrcode": signedInvoice['invoiceQRCode'],
                     "data": stats},
                    status=200)
            else:
                return Response({"status": "400", "Message": "Invalid Json Body Data", "data": zlx.error_messages},
                                status=400)
        except Exception as e:
            print(e)
            return Response({"status": "400", "Message": "Fail", "data": ""}, status=400)


class ProductionClearance(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):

        results = invoiceStep1().data
        return Response(results)

    def post(self, request, *args, **kwargs):
        try:
            c = BusinessLocation.objects.filter(
                authentication_token=self.request.META.get('HTTP_SECRET')).first()

            if c == None:
                return Response({"status": "400", "Message": "Fail", "data": "Invalid Version Code"}, status=400)

            if 'invoice' == request.data['invoice']['documentType']:
                zlx = invoiceStep1(data=request.data)
                invoiceData = invoices(request.data['invoice']['invoiceType'],
                                       request.data['invoice']['documentType'], **request.data)
            elif 'debit_note' == request.data['invoice']['documentType']:
                zlx = debitNote1(data=request.data)
                invoiceData = debitNote(request.data['invoice']['invoiceType'],
                                        request.data['invoice']['documentType'], **request.data)
            else:
                zlx = creditNote1(data=request.data)
                invoiceData = creditNote(request.data['invoice']['invoiceType'],
                                         request.data['invoice']['documentType'], **request.data)
            if zlx.is_valid():
                signedInvoice = sign_xml_document(invoiceData, c.production.private_key,
                                                  c.production.x509_base64)

                invoice = {"invoiceHash": signedInvoice['invoiceHash'],
                           "uuid": request.data['uuid'], "invoice": signedInvoice['invoiceXml']}
                stats = ZatcaClearance(c.production.x509_certificate, c.production.x509_secret, invoice, "production")
                return Response(
                    {"status": "200", "Message": "Success", "qrcode": signedInvoice['invoiceQRCode'],
                     "data": stats},
                    status=200)
            else:
                return Response({"status": "400", "Message": "Invalid Json Body Data", "data": zlx.error_messages},
                                status=400)
        except Exception as e:
            print(e)
            return Response({"status": "400", "Message": "Fail", "data": ""}, status=400)
