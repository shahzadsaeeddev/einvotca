from rest_framework import serializers
from transactions.models import  JournalLine
from products.models import Categories, ProductItem
from neksio_api.models import Customers

from ..models import JournalProductDetail


class RequestNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalLine
        fields = ['id', 'invoice_no']


class IMEINumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalProductDetail
        fields = ['id', 'ime_number']


class ServicesItemsShortSerializer(serializers.ModelSerializer):
    thumbnail = serializers.FileField(source='image_url.thumbnail', read_only=True)
    tax_category = serializers.IntegerField(source='tax_category.tax_percent', read_only=True)

    class Meta:
        model = ProductItem
        fields = ['id', 'thumbnail', 'name', 'category', 'price', 'description', 'tax_applied',
                  'tax_category']
        extra_kwargs = {'image_url': {'write_only': True}}


class CategoriesShortSerializer(serializers.ModelSerializer):
    thumbnail = serializers.FileField(source='image_url.thumbnail', read_only=True)

    class Meta:
        model = Categories
        fields = ['id', 'thumbnail', 'name']


class CustomersShortSerializer(serializers.ModelSerializer):
    thumbnail = serializers.FileField(source='photo.thumbnail', read_only=True)

    class Meta:
        model = Customers
        fields = ['id', 'thumbnail', 'name', 'phone', 'email']





