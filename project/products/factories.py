import factory
from factory import LazyAttribute
from factory.django import DjangoModelFactory
from .models import ProductItem,Categories, PromoCodes, UnitOfMeasurement, SalePriceSlot
from neksio_api.models import BusinessProfile, TaxTypes, MediaFiles

class ProductItemFactory(DjangoModelFactory):
    class Meta:
        model = ProductItem

    name = factory.Faker('word')
    description = factory.Faker('sentence')
    cost_price_slot = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    item_type = factory.Iterator(['raw', 'menu', 'sale'])
    tax_applied = factory.Faker('boolean')
    tax_included = factory.Faker('boolean')
    is_service = factory.Faker('boolean')
    tax_included_amount = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    sku = factory.Faker('ean8')
    barcode = factory.Faker('ean13')

    # Foreign keys (can be optional/null)
    image_url = factory.Iterator(MediaFiles.objects.all()) if MediaFiles.objects.exists() else None
    category = factory.Iterator(Categories.objects.all()) if Categories.objects.exists() else None
    promo = factory.Iterator(PromoCodes.objects.all()) if PromoCodes.objects.exists() else None
    unit_of_measurement = factory.Iterator(UnitOfMeasurement.objects.all()) if UnitOfMeasurement.objects.exists() else None
    price_slot = factory.Iterator(SalePriceSlot.objects.all()) if SalePriceSlot.objects.exists() else None
    tax_category = LazyAttribute(lambda o: TaxTypes.objects.get(id="69e89d85-67c8-4dc4-b9a1-43fb337bafc8"))

    # Will be passed dynamically later
    location = None

    @factory.post_generation
    def product_tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.product_tags.set(extracted)

    @factory.post_generation
    def services(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.services.set(extracted)

# pip install factory_boy faker


# from django.contrib.auth import get_user_model
# from products.factories import ProductItemFactory
# from products.models import Tags, Services
#
# User = get_user_model()
#
# # Get the user you want to assign products to
# user = User.objects.get(username='shahzadmehar')  # Change username if needed
# location = user.business_profile  # Assumes this is the user's location
#
# # Many-to-many tags/services
# all_tags = list(Tags.objects.all())
# all_services = list(Services.objects.all())
#
# # Create 200 products
# for _ in range(200):
#     ProductItemFactory(
#         location=location,
#         product_tags=all_tags[:2],    # assign first 2 tags if exists
#         services=all_services[:2],    # assign first 2 services if exists
#     )
#
# print("✅ 200 products created with location:", location)
