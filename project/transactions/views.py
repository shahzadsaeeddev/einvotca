from django.db.models.fields import DecimalField, IntegerField
from django.db.models.functions.comparison import Coalesce, Cast
from django.db.models.functions.math import Abs

from .imports import *
from .models import JournalDetail
from .serializers.ProductEntries import journalCreditNoteInvoiceSerializer
from neksio_api.models import AccountSetting, FinancialAccounts


class ServiceProductsList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        categories = CategoriesShortSerializer(Categories.objects.by_location(self.request.user), many=True).data
        products = ServicesItemsShortSerializer(ProductItem.objects.by_location(self.request.user), many=True).data
        customers = CustomersShortSerializer(Customers.objects.by_location(self.request.user), many=True).data
        payment_types = PaymentTypesSerializer(
            PaymentTypes.objects.filter(location=self.request.user.business_profile), many=True).data

        invoice_data = InvoiceSettings.objects.filter(business=self.request.user.business_profile).filter(
            Q(default=True)).first()
        if invoice_data:

            invoice = InvoiceLoadSerializer(invoice_data).data
        else:
            invoice = []
        data = {
            'categories': categories,
            'products': products,
            'customers': customers,
            'payment_methods': payment_types,
            'invoice': invoice

        }
        return Response(data=data, status=status.HTTP_200_OK)


class JournalLinesListApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JournalLineSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = SaleInvoiceFilter
    search_fields = ['ref_no', 'invoice_no', 'transaction_type', 'transaction_status', 'items_transactions__ime_number']

    def get_queryset(self):
        return JournalLine.objects.by_location(self.request.user).filter(transaction_type="SALE")


class JournalLinesRetrieveApiView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TransactionsGeneralViewSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return JournalLine.objects.by_location(self.request.user).filter(slug=slug)


class SaleRequestNumberApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request_no = request.query_params.get('return_invoice')

        if not request_no:
            return Response({'error': 'Please enter request number'}, status=status.HTTP_400_BAD_REQUEST)

        journal_lines = JournalLine.objects.filter(
            location=request.user.business_profile,
            invoice_no=request_no,
            transaction_type="SALE"
        )

        if not journal_lines.exists():
            return Response({'error': 'No such journal'}, status=status.HTTP_404_NOT_FOUND)

        serializer = journalCreditNoteInvoiceSerializer(journal_lines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PurchaseRequestNumberApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request_no = request.query_params.get('return_invoice')

        if not request_no:
            return Response({'error': 'Please enter request number'}, status=status.HTTP_400_BAD_REQUEST)

        journal_lines = JournalLine.objects.filter(
            location=request.user.business_profile,
            invoice_no=request_no,
            transaction_type="PURCHASE"
        )

        if not journal_lines.exists():
            return Response({'error': 'No such journal'}, status=status.HTTP_404_NOT_FOUND)

        serializer = journalCreditNoteInvoiceSerializer(journal_lines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IMEINumberApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = IMEINumberSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['ime_number']

    def get_queryset(self):
        return JournalProductDetail.objects.filter(location=self.request.user.business_profile)


class JournalLineMasterCreateApiView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JournalLineMasterSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['ref_no', 'invoice_no']

    def perform_create(self, serializer):
        sale = serializer.save(location=self.request.user.business_profile, created_by=self.request.user)
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Sale", action_type="Create",
                                 description=f"Created Sale - Invoice #{sale.invoice_no}, Customer: {sale.party.name}, Amount: {sale.paid_amount}",
                                 ip_address=ip_address)

    def get_queryset(self):
        return JournalLine.objects.by_location(self.request.user)


class PurchaseItemsListApiView(generics.ListAPIView):
    permission_classes = [HasPurchaseInvoiceRoles]
    serializer_class = JournalLineSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PurchaseFilter
    search_fields = ['ref_no', 'invoice_no', 'transaction_type', 'transaction_status', 'items_transactions__ime_number']

    def get_queryset(self):
        return JournalLine.objects.by_location(self.request.user).filter(transaction_type="PURCHASE")


class PurchaseItemsCreateApiView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JournalLinesPurchaseSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['ref_no', 'invoice_no']

    def perform_create(self, serializer):
        purchase = serializer.save(location=self.request.user.business_profile, created_by=self.request.user)
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Purchases", action_type="Create",
                                 description=f"Created Purchase - Invoice #{purchase.invoice_no}, Supplier: {purchase.party.name}, Amount: {purchase.paid_amount}",
                                 ip_address=ip_address)

    def get_queryset(self):
        return JournalLine.objects.by_location(self.request.user)


class CreditNoteListApiView(generics.ListAPIView):
    permission_classes = [HasCreditNoteRoles]
    serializer_class = JournalLineSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = CreditNoteFilter
    search_fields = ['ref_no', 'invoice_no', 'transaction_type', 'transaction_status']

    def get_queryset(self):
        return JournalLine.objects.by_location(self.request.user).filter(transaction_type="CREDIT_NOTE")


class CreditNoteCreateApiView(generics.CreateAPIView):
    permission_classes = [HasCreditNoteRoles]
    serializer_class = CreditNoteSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['invoice_no', 'party__name']

    def perform_create(self, serializer):
        credit_note = serializer.save(location=self.request.user.business_profile, created_by=self.request.user)
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Credit Note", action_type="Create",
                                 description=f"Created Credit Note - Invoice #{credit_note.invoice_no}, Customer: {credit_note.party.name}, Amount: {credit_note.paid_amount}",
                                 ip_address=ip_address)

    def get_queryset(self):
        return JournalLine.objects.by_location(self.request.user).filter(transaction_type="CREDIT_NOTE")


class DebitNoteListApiView(generics.ListAPIView):
    permission_classes = [HasDebitNoteRoles]
    serializer_class = JournalLineSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = DebitNoteFilter
    search_fields = ['ref_no', 'invoice_no', 'transaction_type', 'transaction_status']

    def get_queryset(self):
        return JournalLine.objects.by_location(self.request.user).filter(transaction_type="DEBIT_NOTE")


class DebitNoteCreateApiView(generics.CreateAPIView):
    permission_classes = [HasDebitNoteRoles]
    serializer_class = DebitNoteSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['invoice_no', 'party__name']

    def perform_create(self, serializer):
        debit_note = serializer.save(location=self.request.user.business_profile, created_by=self.request.user)
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Debit Note", action_type="Create",
                                 description=f"Created Debit Note - Invoice #{debit_note.invoice_no}, Supplier: {debit_note.party.name}, Amount: {debit_note.paid_amount}",
                                 ip_address=ip_address)

    def get_queryset(self):
        return JournalLine.objects.by_location(self.request.user).filter(transaction_type="DEBIT_NOTE")


class SalesZatcaReSubmit(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        data = {
            'detail': "success",

        }
        return Response(data=data, status=status.HTTP_200_OK)


class JournalDetailReportListApiView(generics.ListAPIView):
    permission_classes = [HasGeneralJournalReportRoles, HasLegerReportRoles]
    serializer_class = JournalDetailViewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = JournalDetailFilter

    def get_queryset(self):
        return JournalDetail.objects.filter(transaction__location=self.request.user.business_profile).order_by(
            'transaction__created_at')


class TrialBalanceReportApiView(APIView):
    permission_classes = [HasTrailBalanceReportRoles]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response({"error": "start_date and end_date are required."}, status=400)

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        previous_day = start_date - timedelta(days=1)
        location = request.user.business_profile

        current_balance = JournalDetail.objects.filter(transaction__location=location,
                                                       transaction__date_time__date__gte=start_date,
                                                       transaction__date_time__date__lte=end_date).values(
            'account__code', 'account__title', 'account').annotate(amount=Sum('amount'),
                                                                   account_name=Max('account__title'),
                                                                   account_code=Max('account__code')).exclude(amount=0)

        previous_balance = JournalDetail.objects.filter(transaction__location=location,
                                                        transaction__date_time__date__lte=previous_day).values(
            'account__code', 'account__title', 'account').annotate(amount=Sum('amount'),
                                                                   account_name=Max('account__title'),
                                                                   account_code=Max('account__code')).exclude(amount=0)

        current_data = TrialBalanceReportSerializer(current_balance, many=True).data
        previous_data = TrialBalanceReportSerializer(previous_balance, many=True).data

        for entry in current_data:
            entry['prev_amount'] = 0
            entry['last_amount'] = entry['amount']

            for prev_entry in previous_data:
                if entry['account_code'] == prev_entry['account_code']:
                    entry['prev_amount'] = prev_entry['amount']
                    if float(entry['amount']) != float(entry['prev_amount']):
                        entry['last_amount'] = float(entry['amount']) + float(entry['prev_amount'])

        return Response(current_data)


class SaleReportListApiView(generics.ListAPIView):
    permission_classes = [HasSaleReportRoles]
    serializer_class = SalePurchaseReportSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SaleReportFilter

    def get_queryset(self):
        return JournalLine.objects.by_location(self.request.user).filter(transaction_type="SALE")


class PurchaseReportListApiView(generics.ListAPIView):
    permission_classes = [HasPurchaseReportRoles]
    serializer_class = SalePurchaseReportSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SaleReportFilter

    def get_queryset(self):
        return JournalLine.objects.by_location(self.request.user).filter(transaction_type="PURCHASE")


class InventoryReportListApiView(generics.ListAPIView):
    permission_classes = [HasInventoryReportRoles]
    serializer_class = InventoryReportSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = InventoryReportFilter

    def get_queryset(self):
        return JournalLine.objects.by_location(self.request.user)


class DashboardApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return JournalLine.objects.filter(location=user.business_profile)

    def get(self, request, *args, **kwargs):
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not (start_date and end_date):
            end_date = now().date()
            start_date = end_date - timedelta(days=7)
        else:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)

        queryset = self.get_queryset()
        if start_date and end_date:
            queryset = queryset.filter(date_time__date__range=[start_date, end_date])

        sale_price = JournalProductDetail.objects.filter(
            location=user.business_profile,
            invoice__in=queryset,
            invoice__transaction_type="SALE"
        ).aggregate(total=Sum('rate'))['total'] or 0

        sale_return_price = JournalProductDetail.objects.filter(
            location=user.business_profile,
            invoice__in=queryset,
            invoice__transaction_type="CREDIT_NOTE"
        ).aggregate(total=Sum('rate'))['total'] or 0

        final_sale_price = sale_price - sale_return_price

        cost_price = queryset.filter(transaction_type="SALE").aggregate(total=Sum('cost_amount'))['total'] or 0
        cost_return = queryset.filter(transaction_type="CREDIT_NOTE").aggregate(total=Sum('cost_amount'))['total'] or 0

        final_cost = cost_price - cost_return

        profit = final_sale_price - final_cost if final_sale_price > 0 else 0

        daily_sales_qs = queryset.filter(transaction_type="SALE").annotate(day=TruncDay('date_time')).values(
            'day').annotate(total=Sum('paid_amount'), transactions=Count("id")).order_by('day')

        daily_sales_dict = {
            entry["day"].date(): entry for entry in daily_sales_qs
        }

        monthly_sales_data = []
        current_day = start_date
        while current_day <= end_date:
            entry = daily_sales_dict.get(current_day)
            if entry:
                monthly_sales_data.append({
                    "labels": current_day.strftime("%d %b %Y"),
                    "data": entry["total"] or 0,
                    "transactions": entry["transactions"] or 0
                })
            else:
                monthly_sales_data.append({
                    "labels": current_day.strftime("%d %b %Y"),
                    "data": 0,
                    "transactions": 0
                })
            current_day += timedelta(days=1)

        sale_items = queryset.filter(transaction_type="SALE").aggregate(total_payable_Amount=Sum('paid_amount')) or 0

        today = now().date()
        last_week = today - timedelta(days=7)

        customer = Customers.objects.filter(location=user.business_profile, account_type="customer",
                                            deleted=False).count() or 0

        last_week_customer = Customers.objects.filter(location=user.business_profile, account_type="customer",
                                                      created_at__date__gte=last_week, deleted=False).count() or 0

        quantity = ProductItem.objects.by_location(request.user).annotate(stock_qty=Sum('history__quantity')
                                                                          ).filter(stock_qty__gt=0)

        result = quantity.aggregate(quantity__lte=Sum('stock_qty'), total_price=Sum(F('stock_qty') * F('price')))

        out_of_stock = ProductItem.objects.by_location(request.user).annotate(stock_qty=Sum('history__quantity')
                                                                              ).filter(stock_qty__lte=0).count() or 0

        today = now().date()
        today_sales = (queryset.filter(transaction_type="SALE", date_time__date=today)
                       .aggregate(today_total=Sum("tax_exclusive_amount"))
                       .get("today_total") or 0)

        today_items_count = queryset.filter(transaction_type="SALE", date_time__date=today).count()

        account_setting = AccountSetting.objects.filter(location=self.request.user.business_profile).first()
        accounts = FinancialAccounts.objects.filter(id=account_setting.receive_account).first()

        customer_balance = JournalDetail.objects.filter(account__parent=accounts).aggregate(amount=Sum('amount'))[
                             'amount'] or 0

        account_setting = AccountSetting.objects.filter(location=self.request.user.business_profile).first()
        accounts = FinancialAccounts.objects.filter(id=account_setting.payable_account).first()

        supplier_balance = JournalDetail.objects.filter(account__parent=accounts).aggregate(amount=Sum('amount'))[
                             'amount'] or 0

        top_items = (
            JournalProductDetail.objects.filter(location=user.business_profile)
            .values(
                "item__id",
                "item__name",
                "item__category__name",
                "item__image_url__thumbnail",
            )
            .annotate(
                id=F("item__id"),
                iname=F("item__name"),
                category=F("item__category__name"),
                thumbnail=F("item__image_url__thumbnail"),

                sold_quantity=Coalesce(
                    Sum("quantity", filter=Q(invoice__transaction_type="SALE")), 0,
                    output_field=IntegerField()
                ),

                purchased_quantity=Coalesce(
                    Sum("quantity", filter=Q(invoice__transaction_type="PURCHASE")), 0,
                    output_field=IntegerField()
                ),

                total=Coalesce(
                    Sum("invoice__paid_amount", filter=Q(invoice__transaction_type="SALE")), 0,
                    output_field=DecimalField()
                ),
            )
            .annotate(
                remaining_stock=Cast(F("purchased_quantity"), IntegerField()) - Cast(Abs(F("sold_quantity")),
                                                                                     IntegerField())
            )
            .filter(sold_quantity__lt=0)
            .values("id", "iname", "sold_quantity", "total", "remaining_stock", "category", "thumbnail")
            .order_by("sold_quantity")[:3]
        )

        recent_transactions = queryset.filter(date_time__date__range=[start_date, end_date]).order_by(
            '-date_time').values('party__name', 'invoice_no', 'payment_method__name', 'paid_amount', 'date_time')[:4]

        payment_methods_qs = (
            JournalDetail.objects
            .filter(transaction__in=queryset)
            .filter(account__in=PaymentTypes.objects.values("chart_of_account"))
            .annotate(
                adjusted_amount=Case(
                    When(transaction__transaction_type__in=["SALE", "PURCHASE_REFUND"], then=F("amount")),
                    When(transaction__transaction_type__in=["PURCHASE", "SALE_REFUND"], then=F("amount") * -1),
                    default=Value(0),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
            .values(
                payment_method_name=F("transaction__payment_method__name"),
                chart_of_account_id=F("account__id"),
                chart_of_account_title=F("account__title"),
            )
            .annotate(total_amount=Sum("adjusted_amount"))
            .order_by("chart_of_account_title")
        )

        grand_total = sum(pm["total_amount"] for pm in payment_methods_qs) or 1

        payment_methods = []
        for pm in payment_methods_qs:
            total = float(pm["total_amount"] or 0)
            percentage = round((total / float(grand_total)) * 100, 2)
            payment_methods.append({
                "name": pm["payment_method_name"],
                "total": total,
                "percentage": percentage
            })

        return Response({
            'sales': sale_items,
            'today_sales': today_sales,
            'today_items_count': today_items_count,
            'customer': customer,
            'last_week_customer': last_week_customer,
            'inventory_value': result['total_price'] or 0,
            'out_stock': out_of_stock,
            'profit': profit,
            'top_items': top_items,
            'payment_methods': payment_methods,
            'charts': monthly_sales_data,
            'transactions': recent_transactions,
            'customer_balance': customer_balance,
            'supplier_balance': supplier_balance,

        })


class JournalEntryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GeneralEntrySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = JournalEntryFilter
    search_fields = ['ref_no', 'invoice_no', 'date_time']

    def get_queryset(self):
        return JournalLine.objects.by_location(self.request.user).filter(transaction_type="JOURNAL_ENTRY")

    def perform_create(self, serializer):
        journal_entry = serializer.save(location=self.request.user.business_profile, created_by=self.request.user)
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Journal Entry", action_type="Create",
                                 description=f"Created Journal Entry with invoice no #{journal_entry.invoice_no}",
                                 ip_address=ip_address)


class JournalEntryRetrieveApiView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GeneralEntrySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return JournalLine.objects.by_location(self.request.user).filter(slug=slug).filter(
            transaction_type="JOURNAL_ENTRY")


class PaymentEntryListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasPaymentVoucherRoles]
    serializer_class = PaymentEntriesSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['invoice_no', 'ref_no', 'date_time']

    def get_queryset(self):
        return JournalLine.objects.by_location(self.request.user).filter(transaction_type="PAYMENT_VOUCHER")

    def perform_create(self, serializer):
        payment = serializer.save(location=self.request.user.business_profile, created_by=self.request.user)
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Payment Voucher", action_type="Create",
                                 description=f"Created Payment Voucher with invoice no #{payment.invoice_no}",
                                 ip_address=ip_address)


class ReversePaymentVoucherListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReversePaymentReceiptVoucherSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return JournalLine.objects.by_location(self.request.user).filter(
            transaction_type__in=["REVERSE_PAYMENT_VOUCHER", "REVERSE_RECEIPT_VOUCHER", 'REVERSE_JOURNAL_ENTRY'])

    def perform_create(self, serializer):
        serializer.save(location=self.request.user.business_profile, created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        return Response({"message": "Reverse successfully created."}, status=status.HTTP_201_CREATED)


class ReceiptVoucherEntryListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [HasReceiptVoucherRoles]
    serializer_class = ReceiptVoucherSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['invoice_no', 'ref_no', 'date_time']

    def get_queryset(self):
        return JournalLine.objects.by_location(self.request.user).filter(transaction_type="RECEIPT_VOUCHER")

    def perform_create(self, serializer):
        receipt = serializer.save(location=self.request.user.business_profile, created_by=self.request.user)
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Receipt Voucher", action_type="Create",
                                 description=f"Created Receipt Voucher with invoice no #{receipt.invoice_no}",
                                 ip_address=ip_address)


class BalanceSheetReportListApiView(generics.ListAPIView):
    permission_classes = [HasBalanceSheetReportRoles]
    serializer_class = BalanceSheetTreeSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return FinancialAccounts.objects.by_location(self.request.user).filter(parent__isnull=True).exclude(
            is_ordinary=True)


class IncomeStatementReportView(APIView):
    permission_classes = [HasIncomeStatementReportRoles]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        location = request.user.business_profile

        if not start_date or not end_date:
            return Response({"detail": "Please provide both start_date and end_date."}, status=400)

        account_setting = AccountSetting.objects.filter(location=location).first()

        sales_code = account_setting.sales
        cogs_code = account_setting.csg
        tax = account_setting.tax
        expense = account_setting.expense
        income = account_setting.income

        sales = JournalDetail.objects.filter(transaction__location=location,
                                             transaction__date_time__date__gte=start_date,
                                             transaction__date_time__date__lte=end_date,
                                             account_id=sales_code).aggregate(amount=Sum('amount'))

        sales_total = (sales['amount'] or 0)

        cogs = JournalDetail.objects.filter(transaction__location=location,
                                            transaction__date_time__date__gte=start_date,
                                            transaction__date_time__date__lte=end_date,
                                            account_id=cogs_code).aggregate(amount=Sum('amount'))

        cgs_total = (cogs['amount'] or 0)

        tax_data = JournalDetail.objects.filter(transaction__location=location,
                                                transaction__date_time__date__gte=start_date,
                                                transaction__date_time__date__lte=end_date,
                                                account_id=tax).aggregate(amount=Sum('amount'))

        tax_total = (tax_data['amount'] or 0)

        expenses = JournalDetail.objects.filter(transaction__location=location,
                                                transaction__date_time__date__gte=start_date,
                                                transaction__date_time__date__lte=end_date,
                                                account__parent=expense)

        expense_detail = expenses.values('account__title').annotate(amount=Sum('amount'))

        expense_total = expense_detail.aggregate(total=Sum('amount'))['total'] or 0

        income = JournalDetail.objects.filter(transaction__location=location,
                                              transaction__date_time__date__gte=start_date,
                                              transaction__date_time__date__lte=end_date,
                                              account__parent=income)
        income_detail = income.values('account__title').annotate(amount=Sum('amount')).exclude(
            account__title__in=['Sales Revenue'])

        income_total = income_detail.aggregate(total=Sum('amount'))['total']

        gross_profit = abs(sales_total) - cgs_total
        expense = expense_total

        response = {
            "gross_profit": gross_profit,
            "sales": abs(sales_total),
            "cgs": cgs_total,
            "tax": tax_total,
            "expense": expense,
            'expense_detail': list(expense_detail),
            'income': income_total,
            'income_detail': list(income_detail),

        }

        return Response(response)


class OutOfStockReportView(generics.ListAPIView):
    permission_classes = [HasOutStockReportRoles]
    serializer_class = OutOfStockRefundSerializer

    def get_queryset(self):
        quantity = ProductItem.objects.filter(location=self.request.user.business_profile, deleted=False).annotate(
            stock=Sum('history__quantity')).filter(stock__lte=0)
        return quantity


class PaymentVoucherRetrieveApiView(generics.RetrieveAPIView):
    permission_classes = [HasPaymentVoucherRoles]
    serializer_class = PaymentVoucherDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return JournalLine.objects.by_location(self.request.user).filter(slug=slug)


class DayClosingSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        location = request.user.business_profile
        summary = calculate_day_closing_totals(user, location)
        return Response(summary)


class DayClosingCreateApiView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DayClosingSerializer

    def perform_create(self, serializer):
        serializer.save(location=self.request.user.business_profile, user=self.request.user)


class DayClosingListApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DayClosingListSerializer
    pagination_class = StandardResultsSetPagination
    search_fields = ['opening_balance', 'closing_balance', 'user__username']

    def get_queryset(self):
        return DayClosing.objects.by_location(self.request.user)



class PartyOpeningBalanceCreateApiView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PartyOpeningBalanceSerializer

    def perform_create(self, serializer):
        serializer.save(location=self.request.user.business_profile)
