from uuid import UUID

from django.db.models import Sum
from rest_framework import serializers

from .ProductMixins import SaleItemMixins, ProductItemMixins, ItemHistoryMixin
from .models import Categories, Tags, UnitOfMeasurement, ProductItem, PromoCodes, Services, SalePriceSlot, DiningTable, \
    GroupItems
from neksio_api.models import TaxTypes, BusinessProfile, MediaFiles

from transactions.models import JournalProductDetail


class CategoriesSerializer(serializers.ModelSerializer):
    thumbnail = serializers.FileField(source='image_url.thumbnail', read_only=True)

    class Meta:
        model = Categories
        exclude = ['location', 'deleted', 'updated_at']
        extra_kwargs = {'image_url': {'write_only': True}}


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        exclude = ['location', 'deleted']


class UnitOfMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasurement
        exclude = ['location', 'deleted', 'updated_at']


class SalePriceSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalePriceSlot
        exclude = ['location', 'deleted', 'updated_at']


class GroupItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupItems
        fields = ['id', 'child_item', 'quantity']


class ServicesItemsSerializer(ProductItemMixins, serializers.ModelSerializer):
    thumbnail = serializers.FileField(source='image_url.thumbnail', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    quantity = serializers.SerializerMethodField(allow_null=True, read_only=True)
    tax_percentage = serializers.CharField(source='tax_category.tax_percent', read_only=True)
    products_item = GroupItemsSerializer(many=True, required=False, allow_null=True)
    product_tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tags.objects.all(), required=False)
    services = serializers.PrimaryKeyRelatedField(many=True, queryset=Services.objects.all(), required=False)

    class Meta:
        model = ProductItem
        exclude = ['location', 'deleted']
        extra_kwargs = {'image_url': {'write_only': True}}

    def create(self, validated_data):
        products_items = validated_data.pop('products_item', [])
        tags = validated_data.pop('product_tags', [])
        services = validated_data.pop('services', [])
        product_item = ProductItem.objects.create(**validated_data)
        product_item.product_tags.set(tags)
        product_item.services.set(services)
        product_item.save()
        if validated_data.get('item_type') == 'menu':
            group_items = [GroupItems(product=product_item, location=validated_data['location'], **items) for items in
                           products_items]
            GroupItems.objects.bulk_create(group_items)

        return product_item

    def update(self, instance, validated_data):
        products_items = validated_data.pop('products_item', [])
        tags = validated_data.pop('product_tags', [])
        services = validated_data.pop('services', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.product_tags.set(tags)
        instance.services.set(services)
        instance.save()

        GroupItems.objects.filter(product=instance).delete()

        if products_items:
            group_items = [GroupItems(product=instance, location=instance.location, **items) for items in
                           products_items]
            GroupItems.objects.bulk_create(group_items)

        return instance


class SaleItemsSerializer(SaleItemMixins, serializers.ModelSerializer):
    tax_percentage = serializers.CharField(source='tax_category.tax_percent', read_only=True)

    # ime_number = serializers.SerializerMethodField(allow_null=True, read_only=True)

    class Meta:
        model = ProductItem
        exclude = ['location', 'deleted', 'unit_of_measurement', 'tax_category', 'price_slot', 'product_tags',
                   'services', 'promo', 'category', 'barcode', 'sku', 'description', 'extra_data']
        extra_kwargs = {'image_url': {'write_only': True}}


class SaleItemImeSerializer(SaleItemMixins, serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    tax_percentage = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    cost_price_slot = serializers.CharField(read_only=True)
    price = serializers.CharField(read_only=True)
    tax_included_amount = serializers.CharField(read_only=True)
    item_type = serializers.CharField(read_only=True)
    is_service = serializers.BooleanField(read_only=True)
    total_quantity =serializers.CharField( read_only=True)
    sale_price = serializers.CharField(read_only=True)
    cost = serializers.CharField(read_only=True)

    class Meta:
        model = JournalProductDetail
        fields = ['id', 'ime_number', 'tax_percentage', 'name', 'cost_price_slot', 'price', 'tax_included_amount',
                  'item_type', 'is_service', 'slug','total_quantity', 'sale_price', 'cost']


#
class ItemsDetailSerializer(serializers.ModelSerializer):
    thumbnail = serializers.FileField(source='image_url.thumbnail', read_only=True)
    tax_percentage = serializers.CharField(source='tax_category.tax_percent', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    tax_category = serializers.CharField(source='tax_category.name', read_only=True)
    promo = serializers.CharField(source='promo.name', read_only=True)
    unit_of_measurement = serializers.CharField(source='unit_of_measurement.name', read_only=True)
    price_slot = serializers.CharField(source='price_slot.name', read_only=True)

    product_tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='tag_name')
    services = serializers.SlugRelatedField(many=True, read_only=True, slug_field='service_name')

    class Meta:
        model = ProductItem
        exclude = ['location', 'deleted', 'id']


class ItemTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItem
        fields = ['id', 'name']


class PromoCodesSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['location', 'deleted', 'updated_at']
        model = PromoCodes


class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['location', 'deleted']
        model = Services


class DiningTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiningTable
        exclude = ['location', 'deleted']


def is_valid_uuid(value):
    try:
        UUID(str(value))
        return True
    except Exception:
        return False


class ProductsImportSerializer(serializers.ModelSerializer):
    category = serializers.CharField(required=False, allow_blank=True)
    unit_of_measurement = serializers.CharField(required=False, allow_blank=True)
    tax_category = serializers.CharField(required=False, allow_blank=True)
    price_slot = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    tax_amount = serializers.DecimalField(source='tax_included_amount', max_digits=10, decimal_places=2, required=False)
    taxable = serializers.BooleanField(source='tax_applied', required=False)

    class Meta:
        model = ProductItem
        fields = '__all__'

    def create(self, validated_data):
        location = self.context.get("location")

        category_value = validated_data.pop("category", None)
        uom_value = validated_data.pop("unit_of_measurement", None)
        tax_value = validated_data.pop("tax_category", None)
        price_slot_value = validated_data.pop("price_slot", None)

        # ---------------------------
        # Category
        # ---------------------------
        category = None
        if category_value:
            category_value = str(category_value).strip()
            if is_valid_uuid(category_value):
                category = Categories.objects.filter(id=category_value, location=location).first()
            if not category:
                category = Categories.objects.filter(name__iexact=category_value, location=location).first()
            if not category:
                category = Categories.objects.create(name=category_value, location=location)

        # ---------------------------
        # Unit of Measurement
        # ---------------------------
        uom = None
        if uom_value:
            uom_value = str(uom_value).strip()
            if is_valid_uuid(uom_value):
                uom = UnitOfMeasurement.objects.filter(id=uom_value, location=location).first()
            if not uom:
                uom = UnitOfMeasurement.objects.filter(name__iexact=uom_value, location=location).first()
            if not uom:
                uom = UnitOfMeasurement.objects.create(name=uom_value, location=location, unit_value=1)
        else:
            # default fallback
            uom = UnitOfMeasurement.objects.filter(name__iexact="pcs", location=location).first()
            if not uom:
                uom = UnitOfMeasurement.objects.create(name="pcs", unit_value=1, location=location)

        # ---------------------------
        # Tax Category
        # ---------------------------
        tax = None
        if tax_value:
            tax_value = str(tax_value).strip()
            if is_valid_uuid(tax_value):
                tax = TaxTypes.objects.filter(id=tax_value).first()
            if not tax:
                tax = TaxTypes.objects.filter(name__iexact=tax_value).first()
            if not tax:
                tax = TaxTypes.objects.create(name=tax_value)
        else:
            tax = TaxTypes.objects.filter(name__iexact="No Tax").first()
            if not tax:
                tax = TaxTypes.objects.create(name="No Tax")

        # ---------------------------
        # Price Slot
        # ---------------------------
        price_slot = None
        if price_slot_value:
            price_slot_value = str(price_slot_value).strip()
            if is_valid_uuid(price_slot_value):
                price_slot = SalePriceSlot.objects.filter(id=price_slot_value, location=location).first()
            if not price_slot:
                price_slot = SalePriceSlot.objects.filter(name__iexact=price_slot_value, location=location).first()
            if not price_slot:
                price_slot = SalePriceSlot.objects.create(name=price_slot_value, location=location)
        else:
            price_slot = SalePriceSlot.objects.filter(name__iexact="Default", location=location).first()
            if not price_slot:
                price_slot = SalePriceSlot.objects.create(name="Default", location=location)

        # ---------------------------
        # Final Product Creation
        # ---------------------------
        return ProductItem.objects.create(
            category=category,
            unit_of_measurement=uom,
            tax_category=tax,
            price_slot=price_slot,
            location=location,
            **validated_data
        )

# class ProductsImportSerializer(serializers.ModelSerializer):
#     category = serializers.CharField(required=False, allow_blank=True)
#     unit_of_measurement = serializers.CharField(required=False, allow_blank=True)
#     tax_category = serializers.CharField(required=False, allow_blank=True)
#     price_slot = serializers.CharField(required=False, allow_blank=True)
#     price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
#     tax_amount = serializers.DecimalField(source='tax_included_amount', max_digits=10, decimal_places=2, required=False)
#     taxable = serializers.BooleanField(source='tax_applied', required=False)
#
#     class Meta:
#         model = ProductItem
#         fields = '__all__'
#
#     def create(self, validated_data):
#         category_value = validated_data.pop("category", None)
#         print(category_value)
#         uom_value = validated_data.pop("unit_of_measurement", None)
#         tax_value = validated_data.pop("tax_category", None)
#         price_slot_value = validated_data.pop("price_slot", None)
#         location = self.context.get("location")
#
#         category = None
#         if category_value:
#             category_value = str(category_value).strip()
#             category = (
#                     Categories.objects.filter(id=category_value, location=location).first()
#                     or Categories.objects.filter(name=category_value, location=location).first()
#             )
#             if not category:
#                 category = Categories.objects.create(name=category_value, location=location)
#
#         uom = None
#         if uom_value:
#             uom_value = str(uom_value).strip()
#             uom = (
#                     UnitOfMeasurement.objects.filter(id=uom_value, location=location).first()
#                     or UnitOfMeasurement.objects.filter(name=uom_value, location=location).first()
#             )
#             if not uom:
#                 uom = UnitOfMeasurement.objects.create(name=uom_value, location=location, unit_value=1)
#
#         tax = None
#         if tax_value:
#             tax_value = str(tax_value).strip()
#             tax = (
#                     TaxTypes.objects.filter(id=tax_value).first()
#                     or TaxTypes.objects.filter(name=tax_value).first()
#             )
#             if not tax:
#                 tax = TaxTypes.objects.create(name=tax_value)
#
#         price_slot = None
#         if price_slot_value:
#             price_slot_value = str(price_slot_value).strip()
#             price_slot = (
#                     SalePriceSlot.objects.filter(id=price_slot_value, location=location).first()
#                     or SalePriceSlot.objects.filter(name=price_slot_value, location=location).first()
#             )
#             if not price_slot:
#                 price_slot = SalePriceSlot.objects.create(name=price_slot_value, location=location)
#
#         return ProductItem.objects.create(category=category, unit_of_measurement=uom, tax_category=tax,
#                                           price_slot=price_slot, location=location, **validated_data, )


class ProductExportSerializer(serializers.ModelSerializer):
    category = serializers.CharField()
    unit_of_measurement = serializers.CharField()
    tax_category = serializers.CharField()

    class Meta:
        model = ProductItem
        fields = ['name', 'description', 'item_type', 'image_url', 'cost_price_slot', 'price', 'tax_applied',
                  'tax_included_amount', 'category', 'unit_of_measurement', 'tax_category']

    def create(self, validated_data):
        category_name = validated_data.pop('category', None)
        uom_name = validated_data.pop('unit_of_measurement', None)
        tax_name = validated_data.pop('tax_category', None)
        location = validated_data.pop('location', None)

        category = Categories.objects.filter(name=category_name).first()
        if not category:
            category = Categories.objects.create(name=category_name, location=location)

        uom = UnitOfMeasurement.objects.filter(name=uom_name).first()
        if not uom:
            uom = UnitOfMeasurement.objects.create(name=uom_name, location=location, unit_value=1)

        tax = TaxTypes.objects.filter(name=tax_name).first()

        product = ProductItem.objects.create(category=category, unit_of_measurement=uom, tax_category=tax,
                                             **validated_data)
        return product


class ProductJournalDetailsSerializer(serializers.ModelSerializer):
    transaction_type = serializers.CharField(source='invoice.transaction_type', read_only=True)
    date_time = serializers.DateTimeField(source='invoice.date_time', read_only=True)
    invoice_no = serializers.CharField(source='invoice.invoice_no', read_only=True)
    party_name = serializers.CharField(source='invoice.party.name', read_only=True)

    class Meta:
        model = JournalProductDetail
        fields = [
            'transaction_type', 'invoice_no', 'date_time', 'party_name',
            'rate', 'quantity', 'discount', 'tax_amount', 'total', 'cost', 'ime_number'
        ]


class ItemHistorySerializer(ItemHistoryMixin, serializers.ModelSerializer):
    history = ProductJournalDetailsSerializer(many=True, read_only=True)
    stock = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductItem
        exclude = ['location', 'deleted', 'tax_category', 'price_slot', 'services', 'tax_included_amount', 'category',
                   'unit_of_measurement', 'product_tags', 'promo', 'extra_data']
