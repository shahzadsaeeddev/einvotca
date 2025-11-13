from rest_framework import serializers
from transactions.models import DayClosing, DayClosingDetail
from django.db import transaction


class DayClosingListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = DayClosing
        fields = ['slug', 'opening_balance', 'closing_balance', 'sales', 'discount', 'returns', 'user']


class DayClosingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayClosingDetail
        fields = ['payment_type', 'amount']


class DayClosingSerializer(serializers.ModelSerializer):
    closing_detail = DayClosingDetailSerializer(many=True)
    class Meta:
        model = DayClosing
        fields = ['slug', 'opening_balance', 'closing_balance', 'sales', 'discount', 'returns', 'closing_detail']


    def create(self, validated_data):
        closing_detail = validated_data.pop('closing_detail', '')

        with transaction.atomic():
            validated_data.pop('opening_balance')
            day_closing = DayClosing.objects.create(opening_balance=validated_data['closing_balance'], **validated_data)

            closing_detail = [DayClosingDetail(day_closing=day_closing, location=validated_data['location'], **detail) for detail in closing_detail]
            DayClosingDetail.objects.bulk_create(closing_detail)

        return day_closing