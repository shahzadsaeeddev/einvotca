import csv
from io import TextIOWrapper
from .models import WhatsappContacts


def import_contacts_from_csv(file, company, connection=None):
    reader = csv.DictReader(TextIOWrapper(file, encoding="utf-8"))
    for row in reader:
        number = row.get("number") or row.get("phone") or None
        name = row.get("name") or row.get("Name") or None

        if number:
            WhatsappContacts.objects.get_or_create(
                location=company,
                connection=connection,
                number=number.strip(),
                defaults={"name": name.strip() if name else None}
            )


def import_contacts_from_vcf(file, company, connection=None):
    vcard_data = file.read().decode("utf-8")
    contacts = vcard_data.split("BEGIN:VCARD")

    for contact in contacts:
        if "TEL:" in contact:
            lines = contact.splitlines()
            name = None
            number = None
            for line in lines:
                if line.startswith("FN:"):
                    name = line.replace("FN:", "").strip()
                elif line.startswith("TEL:"):
                    number = line.replace("TEL:", "").strip()

            if number:
                WhatsappContacts.objects.get_or_create(
                    location=company,
                    connection=connection,
                    number=number,
                    defaults={"name": name}
                )

