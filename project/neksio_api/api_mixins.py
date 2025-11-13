from neksio_api.models import Suppliers, Customers
from transactions.models import JournalLine, JournalDetail
from rest_framework.response import Response
from rest_framework import status

class PreventDeleteIfLinkedMixin:
    related_model = JournalLine
    related_field = 'party'
    linked_error_message = "This record is linked to an invoice and cannot be deleted."

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.related_model.objects.filter(**{self.related_field: instance}).exists():
            return Response(
                {"error": self.linked_error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



class DeleteWithAccountMixin:

    account_field = "chart_of_account"

    def perform_destroy(self, instance):
        chart_of_account = getattr(instance, self.account_field, None)

        super().perform_destroy(instance)

        if chart_of_account:
            is_referenced = (
                JournalLine.objects.filter(party__chart_of_account=chart_of_account).exists()
                or JournalDetail.objects.filter(account=chart_of_account).exists()
                or Suppliers.objects.filter(chart_of_account=chart_of_account).exists()
                or Customers.objects.filter(chart_of_account=chart_of_account).exists()
            )

            if not is_referenced:
                chart_of_account.delete()