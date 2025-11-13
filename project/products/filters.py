from django_filters import rest_framework as filters

from products.models import ProductItem


class ProductItemsFilter(filters.FilterSet):
    stock_gt = filters.NumberFilter(field_name='stock_quantity', lookup_expr='gte')
    stock_lt = filters.NumberFilter(field_name='stock_quantity', lookup_expr='lte')

    class Meta:
        model = ProductItem
        fields = ['item_type', 'category__id', 'stock_gt', 'stock_lt']

