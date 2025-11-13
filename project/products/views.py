from django.contrib.postgres.aggregates import ArrayAgg
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Sum, ExpressionWrapper, DecimalField, F, Value, OuterRef, Subquery
from django.db.models.functions.comparison import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from transactions.models import JournalProductDetail
from accounts.permissions import HasProductsRoles, HasProductsAttributesRoles
from neksio_api.models import TaxTypes
from neksio_api.serializers.MasterDataSerializers import TaxTypesSerializer
from .filters import ProductItemsFilter
from .models import Categories, Tags, UnitOfMeasurement, Services, PromoCodes, ProductItem, SalePriceSlot, DiningTable
from .serializer import (CategoriesSerializer, TagsSerializer, UnitOfMeasurementSerializer,
                         ServicesSerializer, ServicesItemsSerializer, PromoCodesSerializer, SalePriceSlotSerializer,
                         DiningTableSerializer, ProductExportSerializer, ItemHistorySerializer, ItemTypeSerializer,
                         ItemsDetailSerializer, SaleItemsSerializer, SaleItemImeSerializer,
                         )
from utilities.modelMixins import StandardResultsSetPagination

from .tasks import import_product
from neksio_api.tasks import activity_logs_task


# Create your views here.
class CategoryListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [HasProductsAttributesRoles]
    serializer_class = CategoriesSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def perform_create(self, serializer):
        category = serializer.save(location=self.request.user.business_profile)

        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(user_id=self.request.user.id, location_id=self.request.user.business_profile.id,
                                 module="Category",
                                 action_type="Create", description=f"Created Category: {category.name}",
                                 ip_address=ip_address)

    def get_queryset(self):
        return Categories.objects.by_location(self.request.user)


class CategoryRetrieveUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CategoriesSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return Categories.objects.by_location(self.request.user).filter(slug=slug)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)

        category = self.get_object()
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Category", action_type="Update",
                                 description=f"Updated Category: {category.name}", ip_address=ip_address)

        return response

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        category_name = category.name
        response = super().destroy(request, *args, **kwargs)
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Category", action_type="delete",
                                 description=f"Delete Category: {category_name}", ip_address=ip_address)
        return response


class TagsListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [HasProductsAttributesRoles]
    serializer_class = TagsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['tag_name']

    def get_queryset(self):
        return Tags.objects.by_location(self.request.user)

    def perform_create(self, serializer):
        tags = serializer.save(location=self.request.user.business_profile)
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Tags", action_type="Create", description=f"Created Tags: {tags.tag_name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))


class TagsRetrieveUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TagsSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return Tags.objects.by_location(self.request.user).filter(slug=slug)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        tags = self.get_object()
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Tags", action_type="Update", description=f"Updated Tags: {tags.tag_name}",
                                 ip_address=ip_address)
        return response

    def destroy(self, request, *args, **kwargs):
        tags = self.get_object()
        tag_name = tags.tag_name
        response = super().destroy(request, *args, **kwargs)
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Tags", action_type="Delete", description=f"Deleted Tag: {tag_name}",
                                 ip_address=ip_address)
        return response


class UnitOfMeasurementListCreateApiView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UnitOfMeasurementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['unit_name']

    def get_queryset(self):
        return UnitOfMeasurement.objects.by_location(self.request.user)

    def perform_create(self, serializer):
        serializer.save(location=self.request.user.business_profile)
        return serializer.data


class UnitOfMeasurementRetrieveUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UnitOfMeasurementSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return UnitOfMeasurement.objects.by_location(self.request.user).filter(slug=slug)


class ServicesListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [HasProductsAttributesRoles]
    serializer_class = ServicesSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['service_name']

    def perform_create(self, serializer):
        services = serializer.save(location=self.request.user.business_profile)
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Services", action_type="Create",
                                 description=f"Created Services: {services.service_name}", ip_address=ip_address)

    def get_queryset(self):
        return Services.objects.by_location(self.request.user)


class ServicesRetrieveUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ServicesSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return Services.objects.by_location(self.request.user).filter(slug=slug)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        services = self.get_object()
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Services", action_type="Update",
                                 description=f"Updated Service: {services.service_name}",
                                 ip_address=ip_address)
        return response

    def destroy(self, request, *args, **kwargs):
        service = self.get_object()
        service_name = service.service_name
        response = super().destroy(request, *args, **kwargs)
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Service", action_type="Delete", description=f"Deleted Service: {service_name}",
                                 ip_address=ip_address)
        return response


class PromoCodesListCreateApiView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PromoCodesSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def perform_create(self, serializer):
        serializer.save(location=self.request.user.business_profile)
        return serializer.data

    def get_queryset(self):
        return PromoCodes.objects.by_location(self.request.user)


class PromoCodesRetrieveUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PromoCodesSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return PromoCodes.objects.by_location(self.request.user).filter(slug=slug)


class ProductItemsListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [HasProductsRoles]
    serializer_class = ServicesItemsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductItemsFilter
    search_fields = ['name', 'item_type', 'history__ime_number']

    def perform_create(self, serializer):
        product = serializer.save(location=self.request.user.business_profile)

        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(user_id=self.request.user.id, location_id=self.request.user.business_profile.id,
                                 module="Product",
                                 action_type="Create", description=f"Created product: {product.name}",
                                 ip_address=ip_address)

    def get_queryset(self):
        return (ProductItem.objects.by_location(self.request.user).annotate(
            stock_quantity=Coalesce(Sum('history__quantity'), 0, output_field=DecimalField()))
                .order_by('-created_at'))


class ProductItemsReportApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        quantity = ProductItem.objects.by_location(request.user).annotate(stock_qty=Sum('history__quantity')
                                                                          ).filter(stock_qty__gt=0)

        result = quantity.aggregate(quantity=Sum('stock_qty'), total_price=Sum(F('stock_qty') * F('price')),
                                    total_cost=Sum(F('stock_qty') * F('cost_price_slot')))

        items = ProductItem.objects.by_location(self.request.user).count()

        return Response({
            'items': items,
            'quantity': result['quantity'] or 0,
            'total_price': result['total_price'] or 0,
            'total_cost': result['total_cost'] or 0,
        })


class ProductItemsRetrieveUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasProductsRoles]
    serializer_class = ServicesItemsSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return ProductItem.objects.by_location(self.request.user).filter(slug=slug)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)

        product = self.get_object()
        ip_address = request.META.get('REMOTE_ADDR')

        activity_logs_task.delay(location_id=request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Product", action_type="Update", description=f"Updated product: {product.name}",
                                 ip_address=ip_address)
        return response

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product_name = product.name
        response = super().destroy(request, *args, **kwargs)

        ip_address = request.META.get('REMOTE_ADDR')

        activity_logs_task.delay(location_id=request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Product", action_type="Delete", description=f"Deleted product: {product_name}",
                                 ip_address=ip_address)
        return response


class ProductItemsRetrieveApiView(generics.RetrieveAPIView):
    permission_classes = [HasProductsRoles]
    serializer_class = ItemsDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return ProductItem.objects.by_location(self.request.user).filter(slug=slug)


class SalePriceSlotListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SalePriceSlotSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return SalePriceSlot.objects.by_location(self.request.user)

    def perform_create(self, serializer):
        serializer.save(location=self.request.user.business_profile)
        return serializer.data


class SalePriceSlotRetrieveUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SalePriceSlotSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return SalePriceSlot.objects.by_location(self.request.user).filter(slug=slug)


class DiningTableListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DiningTableSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['table_number', 'status']

    def get_queryset(self):
        return DiningTable.objects.by_location(self.request.user)

    def perform_create(self, serializer):
        table = serializer.save(location=self.request.user.business_profile)
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Dining Table", action_type="Create",
                                 description=f"Updated table: {table.table_number}", ip_address=ip_address)


class DiningTableRetrieveUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DiningTableSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return DiningTable.objects.by_location(self.request.user).filter(slug=slug)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        table = self.get_object()
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Dining Table", action_type="Update",
                                 description=f"Updated Table: {table.table_number}",
                                 ip_address=ip_address)
        return response

    def destroy(self, request, *args, **kwargs):
        table = self.get_object()
        table_number = table.table_number
        response = super().destroy(request, *args, **kwargs)
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Dining Table", action_type="Delete",
                                 description=f"Deleted Dining table: {table_number}",
                                 ip_address=ip_address)
        return response


class PurchaseProductsMasterListApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SaleItemsSerializer

    def get_queryset(self):
        return ProductItem.objects.by_location(self.request.user)


class SaleProductsMasterListApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SaleItemImeSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['ime_number', 'item__name']

    def get_queryset(self):
        model = JournalProductDetail
        field_names = {f.name for f in model._meta.get_fields() if hasattr(f, "attname")}
        order_fields = ("created_at", "id") if "created_at" in field_names else ("id",)

        base = model.objects.filter(
            invoice__location=self.request.user.business_profile
        )
        def first_for_item(field: str) -> Subquery:
            return Subquery(
                model.objects.filter(
                    item=OuterRef("item"),
                    ime_number=OuterRef("ime_number"),
                    invoice__location=self.request.user.business_profile,
                )
                .order_by(*order_fields)
                .values(field)[:1]
            )
        qs = (
            base.values("item", "ime_number")
            .annotate(
                name=F("item__name"),
                tax_percentage=F("item__tax_category__tax_percent"),
                cost_price_slot=F("item__cost_price_slot"),
                price=F("item__price"),
                tax_included_amount=F("item__tax_included_amount"),
                item_type=F("item__item_type"),
                is_service=F("item__is_service"),
                total_quantity=Sum("quantity"),
                id=F("item__id"),
                slug=first_for_item("slug"),
                sale_price=first_for_item("sale_price"),
                cost=first_for_item("rate"),
            )
            .filter(total_quantity__gte=1)
        )

        return qs


class ManuItemsTypeListApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemTypeSerializer

    def get_queryset(self):
        return ProductItem.objects.by_location(self.request.user)


class importProductApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': 'CSV file is required.'}, status=status.HTTP_400_BAD_REQUEST)

        path = default_storage.save('items/product_import.csv', ContentFile(file.read()))
        user = self.request.user
        location_id = user.business_profile.id
        import_product.delay(path, location_id)

        return Response({"detail": "Item Import Scheduled"}, status=status.HTTP_202_ACCEPTED)


class ExportProductApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = ProductItem.objects.filter(location=self.request.user.business_profile)
        serializer = ProductExportSerializer(items, many=True)
        data = serializer.data
        return Response(status=200, data=data)


class ItemHistoryApiView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemHistorySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return ProductItem.objects.by_location(self.request.user).filter(slug=slug)


class ProductFormInitApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_location = self.request.user.business_profile

        data = {
            "categories": CategoriesSerializer(Categories.objects.filter(location=user_location), many=True).data,
            "umo": UnitOfMeasurementSerializer(UnitOfMeasurement.objects.filter(location=user_location),
                                               many=True).data,
            "price_slot": SalePriceSlotSerializer(SalePriceSlot.objects.filter(location=user_location), many=True).data,
            "tags": TagsSerializer(Tags.objects.filter(location=user_location), many=True).data,
            "service": ServicesSerializer(Services.objects.filter(location=user_location), many=True).data,
            "promo": PromoCodesSerializer(PromoCodes.objects.filter(location=user_location), many=True).data,
            "tax_type": TaxTypesSerializer(TaxTypes.objects.filter(location=user_location), many=True).data,
        }
        return Response(data, status=status.HTTP_200_OK)
