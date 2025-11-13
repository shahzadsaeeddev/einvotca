from django.db import models
import uuid

from rest_framework.pagination import PageNumberPagination
from django.core.mail import send_mail



def send_notification_email(subject, message):
    send_mail(subject, message, 'einvotca@gmail.com', ['bilaljmal@gmail.com', 'social@neksio.com'])


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class ExtraFields(TimestampMixin):
    deleted = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, default=uuid.uuid4, editable=False)

    location = models.ForeignKey('neksio_api.BusinessProfile', on_delete=models.CASCADE, blank=True, null=True,
                                 related_name="%(class)s_data")

    class Meta:
       abstract = True

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.save()

    # def soft_delete(self):
    #     self.deleted = True
    #     self.save()
    #
    # def delete(self, *args, **kwargs):
    #     raise NotImplementedError("Use .soft_delete() instead of delete()")


class RequestMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = self.context.get("request")


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class DefaultFilterManager(models.Manager):
    def by_location(self, user):
        return self.filter(location=user.business_profile).filter(deleted=False)


class CustomerFilterManager(models.Manager):
    def by_location(self, user):
        return self.filter(location=user.business_profile).filter(deleted=False).filter(account_type='customer')


class SupplierFilterManager(models.Manager):
    def by_location(self, user):
        return self.filter(location=user.business_profile).filter(deleted=False).filter(account_type='supplier')
