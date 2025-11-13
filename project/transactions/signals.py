from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import JournalLine
from django.db import transaction

from .tasks import generate_invoice_vector


@receiver(post_save, sender=JournalLine)
def create_vector_invoice(sender, instance, created, **kwargs):
    if not created:
        return
    def _on_transaction_commit():
        generate_invoice_vector.delay(instance.id)

    transaction.on_commit(_on_transaction_commit)
