import factory
from faker import Faker
from .models import Parties, Customers, Suppliers
from neksio_api.models import BusinessProfile

fake = Faker()

class PartiesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Parties

    name = factory.LazyAttribute(lambda x: fake.name())
    email = factory.LazyAttribute(lambda x: fake.email())
    phone = factory.LazyAttribute(lambda x: fake.phone_number())
    address = factory.LazyAttribute(lambda x: fake.address())
    country = factory.LazyAttribute(lambda x: fake.country())

class CustomerFactory(PartiesFactory):
    class Meta:
        model = Customers

    account_type = 'customer'

class SupplierFactory(PartiesFactory):
    class Meta:
        model = Suppliers

    account_type = 'supplier'




# from neksio_api.factories import CustomerFactory, SupplierFactory
# from neksio_api.models import BusinessProfile
# from neksio_api.models import Customers, Suppliers, FinancialAccounts, AccountSetting
# from django.contrib.auth import get_user_model
#
# # 👇 Replace this with the actual user you want
# User = get_user_model()
# user = User.objects.get(username="shahzadmehar")  # Or filter by ID
#
# # 👇 Get location from logged-in user
# user_location = user.business_profile
#
#
# # ✅ Create 200 Customers
# for _ in range(200):
#     account_setting = AccountSetting.objects.get(location=user_location)
#     parent_account = FinancialAccounts.objects.get(id=account_setting.receive_account)
#     financial_account = FinancialAccounts.objects.create(code="", title="Dummy Customer account", type="Asset", parent=parent_account)
#     customer = CustomerFactory(location=user_location, chart_of_account_id=parent_account.id)
#     customer.save()
#
#
# print("✅ 200 Customers and 200 Suppliers created!")



# from neksio_api.factories import CustomerFactory
# from neksio_api.models import BusinessProfile, Customers, FinancialAccounts, AccountSetting
# from django.contrib.auth import get_user_model
#
# User = get_user_model()
# user = User.objects.get(username="shahzadmehar")  # Replace as needed
# user_location = user.business_profile
#
# account_setting = AccountSetting.objects.get(location=user_location)
# parent_account = FinancialAccounts.objects.get(id=account_setting.receive_account)
#
# # Find the last customer code used
# last_account = FinancialAccounts.objects.filter(code__startswith="CU-").order_by('-code').first()
# if last_account and last_account.code:
#     last_num = int(last_account.code.split('-')[-1])
# else:
#     last_num = 0
#
# # ✅ Create 200 Customers with Unique Financial Accounts and Codes
# for i in range(1, 201):
#     current_num = last_num + i
#     account_code = f"CU-{current_num:04d}"
#
#     financial_account = FinancialAccounts.objects.create(
#         code=account_code,
#         title=f"Customer Account {current_num}",
#         type="Asset",
#         parent=parent_account
#     )
#
#     customer = CustomerFactory(
#         location=user_location,
#         chart_of_account=financial_account
#     )
#     customer.save()


