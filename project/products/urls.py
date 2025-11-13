from django.urls import path
from .views import (CategoryListCreateApiView, CategoryRetrieveUpdateDeleteApiView, TagsListCreateApiView,
                    ProductItemsListCreateApiView, ProductItemsRetrieveUpdateDeleteApiView
, TagsRetrieveUpdateDeleteApiView, UnitOfMeasurementRetrieveUpdateDeleteApiView
, UnitOfMeasurementListCreateApiView, ServicesListCreateApiView, ServicesRetrieveUpdateDeleteApiView,
                    PromoCodesListCreateApiView, PromoCodesRetrieveUpdateDeleteApiView,
                    SalePriceSlotListCreateApiView, SalePriceSlotRetrieveUpdateDeleteApiView,
                    DiningTableListCreateApiView, DiningTableRetrieveUpdateDeleteApiView,
                    PurchaseProductsMasterListApiView, importProductApiView, ExportProductApiView, ItemHistoryApiView,
                    ProductItemsReportApiView, SaleProductsMasterListApiView, ManuItemsTypeListApiView,
                    ProductItemsRetrieveApiView, ProductFormInitApiView)

app_name = 'products'
urlpatterns = [

    # ------------------------------------- Manage Categories ------------------------------------- #

    path('categories/', CategoryListCreateApiView.as_view(), name="categories"),
    path('categories/<str:slug>/', CategoryRetrieveUpdateDeleteApiView.as_view(), name="categories-details"),

    # ------------------------------------- Manage Tags ------------------------------------------- #

    path('tags/', TagsListCreateApiView.as_view(), name="tags"),
    path('tags/<str:slug>/', TagsRetrieveUpdateDeleteApiView.as_view(), name="tags-details"),

    # ------------------------------------- Manage Unit Of Measurements --------------------------- #

    path('uoms/', UnitOfMeasurementListCreateApiView.as_view(), name="unit-of-measurements"),
    path('uoms/<str:slug>/', UnitOfMeasurementRetrieveUpdateDeleteApiView.as_view(), name="uoms-details"),

    # ------------------------------------- Manage Services -------------------------------------- #

    path('services/', ServicesListCreateApiView.as_view(), name="services"),
    path('services/<str:slug>/', ServicesRetrieveUpdateDeleteApiView.as_view(), name="service-details"),

    # ------------------------------------- Manage Promo Codes ----------------------------------- #

    path('promo/', PromoCodesListCreateApiView.as_view(), name="promos"),
    path('promo/<str:slug>/', PromoCodesRetrieveUpdateDeleteApiView.as_view(), name="promos-details"),

    # ------------------------------------- Manage Product Items --------------------------------- #

    path('items/', ProductItemsListCreateApiView.as_view(), name="items-service"),
    path('items-report/', ProductItemsReportApiView.as_view(), name="items-report"),
    path('items/<str:slug>/', ProductItemsRetrieveUpdateDeleteApiView.as_view(), name="items-service-details"),
    path('items-detail/<str:slug>/', ProductItemsRetrieveApiView.as_view(), name="items-details"),
    path('import-item/', importProductApiView.as_view(), name="import-item"),
    path('export-item/', ExportProductApiView.as_view(), name="export-item"),
    path('item-history/<str:slug>/', ItemHistoryApiView.as_view(), name="item-history"),

    # ------------------------------------- Manage Price Slots ----------------------------------- #

    path('price-slot/', SalePriceSlotListCreateApiView.as_view(), name="price-slot-list"),
    path('price-slot/<str:slug>/', SalePriceSlotRetrieveUpdateDeleteApiView.as_view(), name="price-slot-list"),

    # ------------------------------------- Manage Dining Table ---------------------------------- #

    path('dining-table/', DiningTableListCreateApiView.as_view(), name="dining-table"),
    path('dining-table/<str:slug>/', DiningTableRetrieveUpdateDeleteApiView.as_view(), name="dining-table-details"),

    # ------------------------------------- Purchase & Sale Products ----------------------------- #

    path('purchase-items/', PurchaseProductsMasterListApiView.as_view(), name="purchase-items"),

    path('sale-items/', SaleProductsMasterListApiView.as_view(), name="purchase-items"),

    path('items-type/', ManuItemsTypeListApiView.as_view(), name="items-type"),

    path("products-init/", ProductFormInitApiView.as_view(), name="products-init"),

]
