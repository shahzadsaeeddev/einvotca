from django.contrib import admin
from .models import Tags, Categories, UnitOfMeasurement, PromoCodes, Services, ProductItem, SalePriceSlot, GroupItems

admin.site.register(Tags)
admin.site.register(UnitOfMeasurement)
admin.site.register(PromoCodes)

@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['location__registered_name']
    list_display = ['name', 'description']


@admin.register(ProductItem)
class ProductItemAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['location__registered_name']
    list_display = ['name', 'item_type', 'cost_price_slot', 'price', 'tax_included']



@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    search_fields = ['service_name']
    list_filter = ['location__registered_name']
    list_display = ['service_name', 'created_at']

admin.site.register(SalePriceSlot)



@admin.register(GroupItems)
class GroupItemsAdmin(admin.ModelAdmin):
    search_fields = ['product__name']
    list_filter = ['location__registered_name']
    list_display = ['created_at']


