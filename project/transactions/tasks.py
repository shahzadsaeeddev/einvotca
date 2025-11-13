from celery.app import shared_task
import re

from .models import JournalLine
# from .vector_handler import QdrantVectorHandler
# QdrantVectorHandler = QdrantVectorHandler()
from .statics.statics import INVOICE_TYPE
@shared_task
def generate_invoice_vector(invoice_id):
    try:
        instance = (
            JournalLine.objects
            .select_related('party', 'location')
            .prefetch_related('items_transactions','journal_lines')
            .get(id=invoice_id)
        )
    except JournalLine.DoesNotExist:
        print(f"JournalLine {invoice_id} not found.")
        return
    items = instance.items_transactions.all()

    journal_lines = instance.journal_lines.all()
    content = ""

    product_summaries = []
    for item in items:
        product_summaries.append(
            f"{item.item_name} ({abs(item.quantity)} unit{'s' if abs(item.quantity) != 1 else ''} at ${item.rate}, total: ${item.total}, tax: ${item.tax_amount})"
        )
    TRANSACTION_TYPES = ['PURCHASE', 'DEBIT_NOTE', 'CREDIT_NOTE', 'SALE']

    if instance.transaction_type in TRANSACTION_TYPES:
        content = (
            f" {INVOICE_TYPE[instance.transaction_type]['TYPE']} {instance.invoice_no} was made on {instance.date_time.strftime('%Y-%m-%d')} "
            f" {INVOICE_TYPE[instance.transaction_type]['PARTY']} {instance.party.name if instance.party else 'Unknown'}. "
            f" {INVOICE_TYPE[instance.transaction_type]['TERM']} include {', '.join(product_summaries)}. "
            f"The total {INVOICE_TYPE[instance.transaction_type]['AMOUNT']} amount was ${abs(instance.payable_amount)}, including ${abs(instance.tax_amount)} in tax. "
            f"An amount of ${instance.paid_amount} was paid, leaving a balance of ${instance.pending_amount}."
        )



    elif instance.transaction_type == "JOURNAL_ENTRY":

        line_summaries = []

        for line in journal_lines:
            amount = abs(line.amount)

            direction = "debited" if line.amount >= 0 else "credited"
            line_summaries.append(f"{line.account.title} {direction} by ${amount:.2f} ,")

        content = (
            f"Journal Entry {instance.invoice_no} was recorded on {instance.date_time.strftime('%Y-%m-%d')}. "
            f"The following entries were made:\n\n"
            f"{chr(10).join(line_summaries)}"

        )



    elif instance.transaction_type in ['PAYMENT_VOUCHER','RECEIPT_VOUCHER',]:
        payment_type = instance.payment_type
        replace_type = payment_type.replace("_", " ").strip().title()
        line_summaries = []
        for line in journal_lines:
            amount = abs(line.amount)
            direction = "debited" if line.amount >= 0 else "credited"
            line_summaries.append(f"{line.account.title}  {direction} by ${amount:.2f}")

        if len(line_summaries) > 1:
            joined_entries = ', '.join(line_summaries[:-1]) + ' and ' + line_summaries[-1]
        else:
            joined_entries = line_summaries[0]

        content = (
            f"{replace_type} payment {instance.invoice_no} was issued on {instance.date_time.strftime('%Y-%m-%d')}, "
            f" with {joined_entries}. "
        )

    name = instance.location.registered_name
    identifier = instance.location_id

    # Normalize name: lowercase, replace non-alphanumeric with underscores, remove extra underscores
    normalized_name = re.sub(r'[^a-z0-9]+', '_', name.strip().lower())
    normalized_name = normalized_name.strip('_')  # Remove leading/trailing underscores

    result = f"{normalized_name}_{identifier}"
    doc = {
            "id": str(instance.id),
            "tenant_id": result,
            "content": content,
            "metadata": {
                "invoice_no": str(instance.invoice_no),
                "customer": instance.party.name if instance.party else "Unknown",
                "date": instance.date_time.strftime('%Y-%m-%d'),
                "transaction_type": instance.transaction_type
            }
        }
    instance.data_collection=doc
    instance.save()
