from neksio_api.factories import SupplierFactory
from neksio_api.models import FinancialAccounts, AccountSetting
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username="shahzadmehar")
user_location = user.business_profile

account_setting = AccountSetting.objects.get(location=user_location)
parent_account = FinancialAccounts.objects.get(id=account_setting.payable_account)

last_account = FinancialAccounts.objects.filter(code__startswith="SU-").order_by('-code').first()
if last_account and last_account.code:
    last_num = int(last_account.code.split('-')[-1])
else:
    last_num = 0

for i in range(1, 201):
    current_num = last_num + i
    account_code = f"SU-{current_num:04d}"

    financial_account = FinancialAccounts.objects.create(
        code=account_code,
        title=f"Supplier Account {current_num}",
        type="Liability",
        parent=parent_account
    )

    customer = SupplierFactory(
        location=user_location,
        chart_of_account=financial_account
    )
    customer.save()

# python manage.py shell < neksio_api/generate_supplier.py