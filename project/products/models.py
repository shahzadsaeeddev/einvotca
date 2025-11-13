from django.contrib.postgres.fields.array import ArrayField
from django.db import models
from utilities.modelMixins import ExtraFields, DefaultFilterManager


class Categories(ExtraFields):
    name = models.CharField(max_length=50)
    description = models.CharField(blank=True, max_length=250)
    image_url = models.ForeignKey('neksio_api.MediaFiles', on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    objects = DefaultFilterManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Tags(ExtraFields):
    tag_name = models.CharField(max_length=50)
    objects = DefaultFilterManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.tag_name


class Services(ExtraFields):
    service_name = models.CharField(max_length=50)
    objects = DefaultFilterManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.service_name


class UnitOfMeasurement(ExtraFields):
    name = models.CharField(max_length=50)
    unit_value = models.PositiveIntegerField(default=0)
    objects = DefaultFilterManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class PromoCodes(ExtraFields):
    name = models.CharField(max_length=50)
    promo_type = models.CharField(max_length=50, choices=[('%', '%'), ('$', '$')])
    value = models.PositiveIntegerField(default=0)
    has_expiry = models.BooleanField(default=False)
    end_date = models.DateField(null=True, blank=True)
    has_expired = models.BooleanField(default=False)

    objects = DefaultFilterManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class SalePriceSlot(ExtraFields):
    name = models.CharField(max_length=50)
    unit_value = models.PositiveIntegerField(default=0)
    value_type = models.CharField(max_length=50, choices=[('%', '%'), ('$', '$')])
    objects = DefaultFilterManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class BaseItems(ExtraFields):
    name = models.CharField(max_length=150)
    image_url = models.ForeignKey('neksio_api.MediaFiles', on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Categories, related_name="%(class)s_data", on_delete=models.SET_NULL, null=True,
                                 blank=True)
    product_tags = models.ManyToManyField(Tags, blank=True, related_name="%(class)s_data")
    promo = models.ForeignKey(PromoCodes, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    extra_data = ArrayField(models.CharField(max_length=150, blank=True, null=True), default=list, blank=True)
    unit_of_measurement = models.ForeignKey(UnitOfMeasurement, on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name="%(class)s_data")

    class Meta:
        abstract = True


class ProductItem(BaseItems):
    ITEM_CHOICES = [
        ("raw", "RAW"),
        ("menu", "Menu"),
        ("sale", "Sale Item"),
        ("device", "Devices"),
        ("accessory", "Accessory"),

    ]
    tax_applied = models.BooleanField(default=False)
    tax_category = models.ForeignKey('neksio_api.TaxTypes', on_delete=models.SET_NULL, null=True, blank=True)
    tax_included = models.BooleanField(default=False)
    price_slot = models.ForeignKey(SalePriceSlot, on_delete=models.SET_NULL, null=True, blank=True)
    cost_price_slot = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_service = models.BooleanField(default=False)
    services = models.ManyToManyField(Services, blank=True)
    item_type = models.CharField(max_length=10, choices=ITEM_CHOICES, default='sale')
    tax_included_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sku = models.CharField(blank=True, null=True, max_length=55, verbose_name='Stock Keeping Unit')
    barcode = models.CharField(null=True, blank=True, max_length=55, verbose_name='Item Barcode')
    objects = DefaultFilterManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class GroupItems(ExtraFields):
    product = models.ForeignKey(ProductItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="products_item")
    child_item = models.ForeignKey(ProductItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="child_items")
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.product.name

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Group Items"
        verbose_name = "Group Items"




class DiningTable(ExtraFields):
    TABLE_STATUS = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('cleaning', 'Cleaning'),
    ]

    table_number = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField()
    status = models.CharField(max_length=50, choices=TABLE_STATUS, default='available')
    qr_code = models.CharField(max_length=100, blank=True, null=True)
    objects = DefaultFilterManager()
