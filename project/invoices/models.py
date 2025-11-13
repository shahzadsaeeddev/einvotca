from django.db import models

from accounts.models import Users, BusinessLocation
import uuid



# Create your models here.
class ZatcaInvoicesProduction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = models.ForeignKey(BusinessLocation, on_delete=models.CASCADE, blank=True,
                                 related_name="productionInvoices")
    invoiceNo = models.CharField(max_length=50)
    invoiceType = models.CharField(max_length=50)
    documentType = models.CharField(max_length=50)
    invoiceUuid = models.CharField(max_length=150)
    invoiceHash = models.TextField(blank=True)
    invoiceBase64 = models.TextField(blank=True)
    invoiceQrcode = models.TextField(blank=True)
    choice = (('success', 'Success'), ('warning', 'warning'), ('failed', 'failed'))
    status = models.CharField(max_length=50, choices=choice)
    status_code = models.PositiveIntegerField()
    message = models.TextField(blank=True)
    createdBy = models.ForeignKey(Users, on_delete=models.CASCADE, blank=True,
                                 related_name="created_by")
    compliance=models.BooleanField(default=False)
    choice = (('sandbox', 'Sandbox'), ('simulation', 'Simulation'), ('production', 'production'))
    invoiceScope = models.CharField(blank=True, choices=choice)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.location.common_name


