def generate_financial_code(location, prefix, bank_model=None):
    from neksio_api.models import FinancialAccounts

    count = (bank_model.objects.filter(location=location).count() + 1) if bank_model else 1
    while True:
        code = f"{prefix}-{count:05d}"
        exists_in_bank = bank_model.objects.filter(location=location, chart_of_account__code=code).exists() if bank_model else False
        exists_in_financial = FinancialAccounts.objects.filter(location=location, code=code).exists()
        if not exists_in_bank and not exists_in_financial:
            return code

        count += 1


def generate_reverse_entry_code(location, prefix, model=None):
    count = (model.objects.filter(location=location).count() + 1) if model else 1
    while True:
        code = f"{prefix}-{count:05d}"
        exists = model.objects.filter(location=location, invoice_no=code).exists()
        if not exists:
            return code
        count += 1
