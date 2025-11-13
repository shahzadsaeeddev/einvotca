import csv
import os

from celery import shared_task
from django.conf import settings

from neksio_api.models import BusinessProfile

from .serializer import ProductsImportSerializer


@shared_task(name="import_product")
def import_product(path, location_id):
    tmp_file = os.path.join(settings.MEDIA_ROOT, path)
    errors = []
    imported = 0

    try:
        location = BusinessProfile.objects.get(id=location_id)
    except BusinessProfile.DoesNotExist:
        return {
            "status": "error",
            "message": f"Location with id {location_id} not found"
        }

    with open(tmp_file, 'r', encoding="utf-8-sig") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            for bool_field in ['taxable', 'online', 'status']:
                if bool_field in row:
                    row[bool_field] = str(row[bool_field]).strip().upper() == "TRUE"

            serializer = ProductsImportSerializer(
                data=row,
                context={'location': location}
            )
            if serializer.is_valid():
                serializer.save()
                imported += 1
            else:
                print("❌ Serializer Errors:\n", serializer.errors)
                errors.append({
                    "row": row,
                    "errors": serializer.errors
                })

    return {
        "status": "completed",
        "imported": imported,
        "errors": errors
    }



