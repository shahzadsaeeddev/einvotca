from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, generics, filters
from rest_framework.response import Response

from .customFilters import InvoiceFilter
from .models import ZatcaInvoicesProduction

from .serializer import ZatcaSandboxInvoiceSerializer, ZatcaSandboxInvoiceDashboardSerializer
from utilities.modelMixins import StandardResultsSetPagination


class ProductionInvoiceView(generics.ListAPIView):
    queryset = ZatcaInvoicesProduction.objects.all()
    serializer_class = ZatcaSandboxInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter,DjangoFilterBackend]
    search_fields = ['invoiceNo', 'invoiceUuid']
    filterset_class=InvoiceFilter



class ProductionInvoiceDashboardView(generics.ListAPIView):
    queryset = ZatcaInvoicesProduction.objects.all()
    serializer_class = ZatcaSandboxInvoiceDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class=InvoiceFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).order_by('invoiceScope')


        scope_status_count = queryset.values('invoiceScope', 'status').annotate(total=Count('id'))
        scope_compliance = queryset.values( 'compliance', 'status').annotate(total=Count('id')).exclude(compliance=False)
        reporting_clearance = queryset.values('invoiceType').annotate(total=Count('id'))
        document_type = queryset.values('documentType').annotate(total=Count('id'))

        # Construct response object
        return Response({

            'compliance': list(scope_compliance),
            'reporting_clearance':list(reporting_clearance),
            'status': list(scope_status_count),
            'documentType':list(document_type)
        })
