from django.db.models.aggregates import Sum

from transactions.models import JournalProductDetail


class ProductItemMixins:
    def get_quantity(self, obj):
        total = JournalProductDetail.objects.filter(item=obj).aggregate(qty=Sum('quantity'))['qty']
        return total or 0


class ItemHistoryMixin:
    def get_stock(self, obj):
        total = JournalProductDetail.objects.filter(item=obj).aggregate(qty=Sum('quantity'))['qty']
        return total or 0


class SaleItemMixins:
    def get_ime_number(self, obj):
        imei_numbers = sum((detail.ime_number for detail in obj.history.all() if detail.ime_number), [])
        return imei_numbers or None

