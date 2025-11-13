import cv2
import numpy as np
from django.shortcuts import get_object_or_404

from .api_mixins import PreventDeleteIfLinkedMixin
from .imports import *
from .media_info import get_media_info
from .utils import import_contacts_from_csv, import_contacts_from_vcf
from .whatsapp_service import send_text_message, send_media_message, send_audio_message


class FinancialAccountCodeGenerateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        prefix = request.query_params.get('type')
        location = request.user.business_profile

        if not prefix:
            return Response({"detail": "Account prefix (`type`) is required in URL, e.g., ?type=SA"},
                            status=status.HTTP_400_BAD_REQUEST)

        prefix = prefix.upper()

        count = JournalLine.objects.filter(location=location, invoice_no__startswith=f"{prefix}-").count() + 1

        generated_code = f"{prefix}-{count:05d}"

        return Response({"code": generated_code}, status=status.HTTP_200_OK)


class DummyDataView(generics.ListCreateAPIView):
    queryset = DummyData.objects.all()
    serializer_class = DummyDataSerializer
    permission_classes = (permissions.IsAuthenticated, HasRolesManager)
    pagination_class = StandardResultsSetPagination


class MediaFilesView(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MediaFilesSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['file_name', 'description']
    filterset_class = MediaFilter

    def perform_create(self, serializer):
        media = serializer.save(location=self.request.user.business_profile)
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Gallery", action_type="create",
                                 description=f"Created Media File {media.file_name}", ip_address=ip_address)

    def get_queryset(self):
        return MediaFiles.objects.by_location(self.request.user).filter(deleted=False)





class MediaFilesListCreateView(generics.CreateAPIView):
    queryset = MediaFiles.objects.all()
    serializer_class = MediaFilesBase64Serializer
    permission_classes = [IsAuthenticated]

    def generate_sketch(self, file):
        file.seek(0)
        img_array = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inverted_image = cv2.bitwise_not(gray_image)
        blurred = cv2.GaussianBlur(inverted_image, (21, 21), sigmaX=0, sigmaY=0)
        inverted_blurred = cv2.bitwise_not(blurred)
        sketch = cv2.divide(gray_image, inverted_blurred, scale=256.0)
        sketch_pil = Image.fromarray(sketch)
        buffer = BytesIO()
        sketch_pil.save(buffer, format="PNG")
        buffer.seek(0)

        return ContentFile(buffer.getvalue(), name="sketch.png")

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            original_file = serializer.validated_data['file']

            sketch_file = self.generate_sketch(original_file)

            serializer.validated_data['file'] = sketch_file

            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class EmailSupportView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmailSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['ticket_number', 'email']

    def get_queryset(self):
        return EmailSupport.objects.filter(email=self.request.user.email)


class CountriesView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CountriesSerializer

    def get_queryset(self):
        return Countries.objects.filter(disabled=False)


class TaxTypeView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TaxTypesSerializer

    def get_queryset(self):
        return TaxTypes.objects.filter(location=self.request.user.business_profile)


class PaymentTypeView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PaymentTypesSerializer

    def get_queryset(self):
        return PaymentTypes.objects.filter(location=self.request.user.business_profile)


class InvoiceSettingView(generics.ListCreateAPIView):
    permission_classes = [HasInvoiceSetupRoles]
    serializer_class = InvoiceSettingSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return InvoiceSettings.objects.filter(business=self.request.user.business_profile)

    def perform_create(self, serializer):
        invoice = serializer.save(business=self.request.user.business_profile)
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Invoice Setup", action_type="create",
                                 description=f"Created Invoice Setting {invoice.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))


class InvoiceSettingDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasInvoiceSetupRoles]
    serializer_class = InvoiceSettingSerializer
    lookup_field = 'id'

    def get_queryset(self):
        id = self.kwargs.get(self.lookup_field)
        return InvoiceSettings.objects.filter(business=self.request.user.business_profile).filter(id=id)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        invoice = self.get_object()
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Invoice Setup", action_type="update",
                                 description=f"Updated Invoice Setting {invoice.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response

    def destroy(self, request, *args, **kwargs):
        invoice = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Invoice Setup", action_type="delete",
                                 description=f"Deleted Invoice Setting {invoice.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response


class MediaFilesDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MediaFilesDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return MediaFiles.objects.by_location(self.request.user).filter(deleted=False).filter(slug=slug)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        media = self.get_object()
        activity_logs_task.delay(location_id=request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Gallery", action_type="update",
                                 description=f"Updated Media File {media.file_name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))

        return response

    def destroy(self, request, *args, **kwargs):
        media = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        activity_logs_task.delay(location_id=request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Gallery", action_type="delete",
                                 description=f"Deleted Media File {media.file_name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))

        return response


class BusinessTypesView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = BusinessTypes.objects.all()
    serializer_class = BusinessTypesSerializer


class BusinessProfileView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer

    def perform_create(self, serializer):
        return serializer.save(context=self.request)


class BusinessProfileRetrieveView(APIView):
    permission_classes = [HasBusinessProfileRoles]

    def get(self, request, *args, **kwargs):
        instance = BusinessProfile.objects.filter(id=self.request.user.business_profile_id).first()
        if instance is not None:
            serializer = BusinessProfileSerializer(instance=instance, many=False)

            return Response(data={"message": "success", "data": serializer.data}, status=200)
        else:
            return Response(data={"message": "profile data not found"}, status=400)


class CurrentPackagePlanView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CurrentPackagePlanSerializer

    def get_object(self):
        return self.request.user.business_profile


class BusinessPaymentsView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = BusinessPaymentsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter

    def get_queryset(self):
        obj = PaymentsHistory.objects.filter(business_profile=self.request.user.business_profile)
        return obj


class BusinessProfileSecretView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        instance = BusinessProfile.objects.filter(id=self.request.user.business_profile_id).first()
        if instance is not None:
            serializer = BusinessProfileSecretSerializer(instance=instance, many=False)

            return Response(data={"message": "success", "data": serializer.data}, status=200)
        else:
            return Response(data={"message": "profile data not found"}, status=400)


class BusinessCurrentBillView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        invoice_count = ZatcaInvoicesProduction.objects.filter(
            location__company=self.request.user.business_profile).count()
        package_plan = self.request.user.business_profile.package_plan
        package = str(package_plan) if package_plan else ""
        rate = getattr(package_plan, 'rate', 0.0)
        try:
            rate = float(rate) if rate is not None else 0.0
        except (ValueError, TypeError):
            rate = 0.0
        # invoice = int(invoice_count) if invoice_count is not None else 0
        # price = rate * invoice if package != 'Demo' else "Free"
        # users_used = Users.objects.filter(business_profile=self.request.user.business_profile).count()
        # locations_used = BusinessLocation.objects.filter(company=self.request.user.business_profile).count()

        return Response(data={
            "invoice": invoice_count,
            "rate": rate,
            "package": package,
            "expiry_date": self.request.user.business_profile.expiry_date,
            "locations_allowed": self.request.user.business_profile.no_of_locations,
            "users_allowed": self.request.user.business_profile.no_of_users,
            "bill_to": self.request.user.business_profile.registered_name,
            "bill": rate
        }, status=200)


# BusinessPackagesSerializer
class BusinessPackagesView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = BusinessPackages.objects.exclude(default_package=True)
    serializer_class = BusinessPackagesSerializer


class CustomersView(generics.ListCreateAPIView):
    permission_classes = [HasCustomersRoles]
    serializer_class = CustomersSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def perform_create(self, serializer):
        customer = serializer.save(location=self.request.user.business_profile)
        ip_address = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Customer", action_type="create",
                                 description=f"Created Customer {customer.name}", ip_address=ip_address)

    def get_queryset(self):
        return Customers.objects.by_location(self.request.user)


class CustomerReportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        account_setting = AccountSetting.objects.filter(location=self.request.user.business_profile).first()
        accounts = FinancialAccounts.objects.filter(id=account_setting.receive_account).first()

        journal_detail = JournalDetail.objects.filter(account__parent=accounts).aggregate(amount=Sum('amount'))[
                             'amount'] or 0

        customers = Customers.objects.by_location(self.request.user).count()

        positive_balance = JournalDetail.objects.filter(account__parent=accounts).values('transaction__party').annotate(
            total_amount=Sum('amount')).filter(total_amount__gt=0).count()

        return Response({'customers': customers, 'amount': journal_detail, 'positive_balance': positive_balance},
                        status=200)


class CustomersDetailView(PreventDeleteIfLinkedMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasCustomersRoles]
    serializer_class = CustomersSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return Customers.objects.by_location(self.request.user).filter(slug=slug)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        customer = self.get_object()
        activity_logs_task.delay(location_id=customer.id, user_id=self.request.user.id, module="Customer",
                                 action_type="update", description=f"Updated Customer {customer.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response

    def delete(self, request, *args, **kwargs):
        customer = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        activity_logs_task.delay(location_id=customer.id, user_id=self.request.user.id, module="Customer",
                                 action_type="deleted", description=f"Deleted Customer {customer.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response


class SuppliersView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SuppliersSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def perform_create(self, serializer):
        supplier = serializer.save(location=self.request.user.business_profile)
        ip = self.request.META.get('REMOTE_ADDR')
        activity_logs_task.delay(location_id=supplier.id, user_id=self.request.user.id, module="Supplier",
                                 action_type="create", description=f"Created Supplier {supplier.name}",
                                 ip_address=ip)

    def get_queryset(self):
        return Suppliers.objects.by_location(self.request.user)


class SupplierReportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        account_setting = AccountSetting.objects.filter(location=self.request.user.business_profile).first()
        accounts = FinancialAccounts.objects.filter(id=account_setting.payable_account).first()

        journal_detail = JournalDetail.objects.filter(account__parent=accounts).aggregate(amount=Sum('amount'))[
                             'amount'] or 0

        suppliers = Suppliers.objects.by_location(self.request.user).count()

        positive_balance = JournalDetail.objects.filter(account__parent=accounts).values('transaction__party').annotate(
            total_amount=Sum('amount')).filter(total_amount__gt=0).count()

        return Response({'supplier': suppliers, 'amount': journal_detail, 'positive_balance': positive_balance},
                        status=200)


class SuppliersDetailView(PreventDeleteIfLinkedMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasSuppliersRoles]
    serializer_class = SuppliersSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return Suppliers.objects.by_location(self.request.user).filter(slug=slug)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        supplier = self.get_object()
        activity_logs_task.delay(location_id=supplier.id, user_id=self.request.user.id, module="Supplier",
                                 action_type="update", description=f"Updated Supplier {supplier.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'), )
        return response

    def delete(self, request, *args, **kwargs):
        supplier = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        activity_logs_task.delay(location_id=supplier.id, user_id=self.request.user.id, module="Supplier",
                                 action_type="deleted", description=f"Deleted Supplier {supplier.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            plan_id = request.data.get('plan_id')
            duration = request.data.get('duration', '')
            if not plan_id:
                return Response(data={"error": "No plan id provided"}, status=400)

            plan = BusinessPackages.objects.filter(id=plan_id).first()
            # if duration:
            #     BusinessPackages.objects.filter(id=plan_id).update(duration=duration)

            if not plan:
                return Response(data={"error": "Plan not found"}, status=400)

            if plan and plan.discount > 0:
                total_price = plan.discount * duration
            else:
                total_price = plan.price * duration

            access_token = get_paypal_access_token()
            url = f"{settings.PAYPAL_API_BASE}/v2/checkout/orders"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            data = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": "USD",
                            "value": str(total_price)
                        }
                    }
                ]
            }
            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 201:
                profile = self.request.user.business_profile
                PaymentsHistory.objects.create(business_profile=profile, package_plan=plan, amount=total_price,
                                               orderID=response.json()['id'], duration=duration)

                return Response(data=response.json(), status=status.HTTP_201_CREATED)
            else:
                return Response(data={
                    "error": response.json(),
                    "message": "Failed to create PayPal order"
                }, status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class CapturePaypalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            order_id = request.data.get('orderID')

            if not order_id:
                return Response(data={"error": "No order id provided"}, status=400)

            access_token = get_paypal_access_token()

            url = f"{settings.PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture"

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            }
            response = requests.post(url, headers=headers)
            if response.status_code == 200:
                profile = self.request.user.business_profile
                PaymentsHistory.objects.filter(business_profile=profile, orderID=request.data['orderID']).update(
                    **request.data, payment_status="success")

                payment = PaymentsHistory.objects.filter(business_profile=profile, orderID=order_id).first()

                request = self.request.user
                auth_token = self.request.META.get('HTTP_AUTHORIZATION')
                if auth_token and auth_token.startswith('Bearer '):
                    auth_token = auth_token.split(' ')[1]

                assigned = payment.package_plan.package_code
                default = request.business_profile.package_plan.package_code

                if profile.package_plan:
                    update_role(auth_token, request.keycloak_uuid, default, assigned)
                    today = datetime.now()
                    expiry_date = today + relativedelta(months=payment.duration)
                    profile.package_plan = payment.package_plan
                    profile.expiry_date = expiry_date
                    profile.save()

                    return Response(data=response.json(), status=status.HTTP_200_OK)
                return Response(response.json(), status=200)
            else:
                return Response(
                    {
                        "error": "Failed to capture PayPal payment",
                        "details": response.json()
                    },
                    status=response.status_code
                )
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class PaymentHistoryListApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentHistorySerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['orderID', 'paid_by__username']

    def get_queryset(self):
        return PaymentsHistory.objects.filter(business_profile=self.request.user.business_profile,
                                              paid_by=self.request.user)


class BankInformationListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [HasBankAccountsRoles]
    serializer_class = BankAccountSerializer
    pagination_class = StandardResultsSetPagination
    search_fields = ['name', ]

    def get_queryset(self):
        return BankAccount.objects.by_location(self.request.user).filter(deleted=False)

    def perform_create(self, serializer):
        banks = serializer.save(location=self.request.user.business_profile)
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Bank Accounts", action_type="create",
                                 description=f"Created {banks.account_title} Bank Account")


class BankBalanceReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        account_setting = AccountSetting.objects.filter(location=self.request.user.business_profile).first()
        accounts = FinancialAccounts.objects.filter(id=account_setting.banks).first()

        journal_detail = JournalDetail.objects.filter(account__parent=accounts).aggregate(amount=Sum('amount'))[
                             'amount'] or 0
        return Response({'amount': journal_detail},
                        status=200)


class BankTransactionHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BankTransactionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['transaction__invoice_no', 'transaction__transaction_type']
    filterset_class = BankTransactionFilter

    def get_queryset(self):
        bank_id = self.kwargs.get("pk")
        try:
            bank = BankAccount.objects.get(id=bank_id)
        except BankAccount.DoesNotExist:
            return JournalDetail.objects.none()

        return JournalDetail.objects.filter(account=bank.chart_of_account).select_related('transaction',
                                                                                          'transaction__party')


class BankInformationRetrieveUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasBankAccountsRoles]
    serializer_class = BankAccountSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_queryset(self):
        return BankAccount.objects.by_location(self.request.user).filter(deleted=False)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        banks = self.get_object()
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Bank Accounts", action_type="update",
                                 description=f"Updated {banks.account_title} Bank Account",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response

    def delete(self, request, *args, **kwargs):
        banks = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Bank Accounts", action_type="delete",
                                 description=f"Deleted {banks.account_title} Bank Account",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response


class InvestorListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [HasInvestorsRoles]
    serializer_class = InvestorSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['title', 'equity_percentage', 'chart_of_account__code']

    def get_queryset(self):
        return Investor.objects.by_location(self.request.user).filter(deleted=False)

    def perform_create(self, serializer):
        investor = serializer.save(location=self.request.user.business_profile)
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Investor", action_type="create",
                                 description=f"Investor created {investor.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))


class InvestorReportApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        account_setting = AccountSetting.objects.filter(location=self.request.user.business_profile).first()
        accounts = FinancialAccounts.objects.filter(id=account_setting.equity).first()

        investor_accounts = FinancialAccounts.objects.filter(investor__isnull=False).distinct()

        investor_amount = JournalDetail.objects.filter(account__in=investor_accounts).aggregate(amount=Sum('amount'))[
                              'amount'] or 0

        # journal_detail = JournalDetail.objects.filter(account_id=accounts).aggregate(amount=Sum('amount'))[
        #                      'amount'] or 0
        investor_count = Investor.objects.by_location(self.request.user).filter(deleted=False).count() or 0

        return Response({
            'amount': investor_amount,
            'investor': investor_count
        }, status=200)


class InvestorRetrieveUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasInvestorsRoles]
    serializer_class = InvestorSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_queryset(self):
        return Investor.objects.by_location(self.request.user)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        investor = self.get_object()
        activity_logs_task.delay(location_id=investor.id, user_id=self.request.user.id, module="Investor",
                                 action_type="update", description=f"Investor updated {investor.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response

    def delete(self, request, *args, **kwargs):
        investor = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        activity_logs_task.delay(location_id=investor.id, user_id=self.request.user.id, module="Investor",
                                 action_type="delete", description=f"Investor deleted {investor.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response


class FinancialAccountsListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [HasFinancialAccountsRoles]
    serializer_class = FinancialAccountsSerializer

    def get_queryset(self):
        return FinancialAccounts.objects.by_location(self.request.user).filter(parent__isnull=True)

    def perform_create(self, serializer):
        financial_account = serializer.save(location=self.request.user.business_profile)
        activity_logs_task.delay(location_id=financial_account.id, user_id=self.request.user.id,
                                 module="Financial Account", action_type="create",
                                 description=f"Financial Account created {financial_account.title}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))


class FinancialAccountsRetrieveUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasFinancialAccountsRoles]
    serializer_class = FinancialAccountsSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_queryset(self):
        return FinancialAccounts.objects.by_location(self.request.user)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        financial_account = self.get_object()
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Financial Account", action_type="update",
                                 description=f"Financial Account updated {financial_account.title}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response

    def delete(self, request, *args, **kwargs):
        financial_account = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Financial Account", action_type="delete",
                                 description=f"Financial Account deleted {financial_account.title}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response


class FinancialAccountsListApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FinancialAccountListSerializer

    def get_queryset(self):
        return FinancialAccounts.objects.by_location(self.request.user)


class FinancialAccountsChildApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FinancialAccountListSerializer

    def get_queryset(self):
        return FinancialAccounts.objects.by_location(self.request.user).filter(parent__isnull=False)


class OpeningBalanceAccountListApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FinancialAccountListSerializer

    def get_queryset(self):
        return FinancialAccounts.objects.by_location(self.request.user).filter(
            title__in=["Opening Balance", "Closing Balance"], parent__isnull=False)


class PayableAccountsApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FinancialAccountListSerializer

    def get_queryset(self):
        return FinancialAccounts.objects.by_location(self.request.user).filter(
            Q(parent__title="Current Asset") | Q(title="Bank") | Q(parent__title="Bank"))


class IncomeExpenseHeadListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [HasIncomeExpenseRoles]
    serializer_class = IncomeExpenseHeadSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = IncomeExpenseFilter
    search_fields = ['name', 'chart_of_account__code', 'type']

    def get_queryset(self):
        return IncomeExpenseHead.objects.by_location(self.request.user).filter(deleted=False)

    def perform_create(self, serializer):
        income = serializer.save(location=self.request.user.business_profile)
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Income Expense", action_type="create",
                                 description=f"Income Expense created {income.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))


class IncomeExpenseHeadRetrieveUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasIncomeExpenseRoles]
    serializer_class = IncomeExpenseHeadSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_queryset(self):
        return IncomeExpenseHead.objects.by_location(self.request.user)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        income = self.get_object()
        activity_logs_task.delay(location_id=request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Income Expense", action_type="update",
                                 description=f"Income Expense updated {income.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response

    def delete(self, request, *args, **kwargs):
        income = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Income Expense", action_type="delete",
                                 description=f"Income Expense deleted {income.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response


class LiabilityAccountsApiView(generics.ListAPIView):
    serializer_class = LiabilityFlatAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        location = user.business_profile
        return AssetLiabilityHead.objects.filter(location=location, chart_of_account__type="Liability")


class AssestLiabilityHeadListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [HasAssetLiabilityRoles]
    serializer_class = AssestLiabilityHeadSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['type']
    search_fields = ['name', 'chart_of_account__code', 'type']

    def get_queryset(self):
        return AssetLiabilityHead.objects.by_location(self.request.user).filter(deleted=False)

    def perform_create(self, serializer):
        liability = serializer.save(location=self.request.user.business_profile)
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Asset Liability", action_type="create",
                                 description=f"Asset Liability created {liability.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))


class AssestLiabilityHeadRetrieveUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasAssetLiabilityRoles]
    serializer_class = AssestLiabilityHeadSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_queryset(self):
        return AssetLiabilityHead.objects.by_location(self.request.user)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        asset = self.get_object()
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Asset Liability", action_type="update",
                                 description=f"Asset Liability updated {asset.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response

    def delete(self, request, *args, **kwargs):
        asset = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Asset Liability", action_type="delete",
                                 description=f"Asset Liability deleted {asset.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response


class AccountSettingListUpdateApiView(APIView):
    permission_classes = [HasAccountSettingRoles]

    def get(self, request):
        account_setting = AccountSetting.objects.filter(location=self.request.user.business_profile).first()
        if account_setting is not None:
            serializer = AccountSettingSerializer(account_setting, many=False)
            return Response(status=200, data=serializer.data)
        else:
            return Response(status=204, data={"details": "No record found"})

    def patch(self, request):

        account_setting = AccountSetting.objects.filter(location=self.request.user.business_profile).first()

        serializer = AccountSettingSerializer(account_setting, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            activity_logs_task.delay(location_id=request.user.business_profile.id, user_id=self.request.user.id,
                                     module="Account Setting", action_type="update",
                                     description=f"Account setting updated",
                                     ip_address=self.request.META.get('REMOTE_ADDR'))
            return Response(serializer.data, status=200)
        return Response(status=406, data=serializer.errors)


class BusinessWhatsappApiView(APIView):
    permission_classes = []

    def get(self, request):
        business_profile = getattr(request.user, 'business_profile', None)

        if business_profile and business_profile.id:
            whatsapp_setting = business_profile.id
            whatsapp_profile = BusinessWhatsappProfile.objects.filter(business_profile_id=whatsapp_setting).first()

            if whatsapp_profile:
                serializer = BusinessWhatsappProfileSerializer(whatsapp_profile)
                return Response({"state": whatsapp_setting, "data": serializer.data}, status=status.HTTP_200_OK)
            return Response({"state": whatsapp_setting, "data": None}, status=status.HTTP_200_OK)

        return Response({"details": "No record found"}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request):
        profile_id = request.data.get("id")

        if not profile_id:
            return Response({"error": "Missing 'id' in request body"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = BusinessWhatsappProfile.objects.get(id=profile_id)
            serializer = BusinessWhatsappProfileSerializer(profile)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except BusinessWhatsappProfile.DoesNotExist:
            return Response({"status": "Connection failed, please try again later"}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request):
        # Make a copy of incoming data
        data = request.data.copy()
        # Try to fetch existing profile
        whatsapp_setting = BusinessWhatsappProfile.objects.filter(
            business_profile=request.user.business_profile
        ).first()
        if whatsapp_setting:
            # Update existing
            serializer = BusinessWhatsappProfileSerializer(
                whatsapp_setting,
                data=data,
                partial=True
            )
        else:
            # Create new
            serializer = BusinessWhatsappProfileSerializer(data=data)

        if serializer.is_valid():
            instance = serializer.save(collections=request.user.collections,
                                       business_profile=request.user.business_profile)

            activity_logs_task.delay(
                location_id=request.user.business_profile.id,
                user_id=request.user.id,
                module="Whatsapp account  ",
                action_type="update" if whatsapp_setting else "create",
                description="Whatsapp setting updated" if whatsapp_setting else "Whatsapp setting created",
                ip_address=request.META.get('REMOTE_ADDR')
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FacebookWebhookApiView(APIView):
    permission_classes = []

    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')

        app_id = os.getenv("APP_ID")
        redirect_url = os.getenv("REDIRECT_URI")
        app_secret = os.getenv("APP_SECRET")

        if not code:
            return Response({"error": "Missing authorization code"}, status=400)
        if not state:
            return Response({"error": "Missing state parameter"}, status=400)
        print(redirect_url)
        # 1️⃣ Exchange code for access token
        token_url = "https://graph.facebook.com/v21.0/oauth/access_token"
        params = {
            "client_id": app_id,
            "redirect_uri": redirect_url,
            "client_secret": app_secret,
            "code": code
        }
        token_response = requests.get(token_url, params=params).json()

        if "access_token" not in token_response:
            return Response({"error": "Failed to fetch access token", "details": token_response}, status=400)
        user_access_token = token_response["access_token"]

        # 2️⃣ Get customer's Facebook business details
        business_accounts = requests.get(
            "https://graph.facebook.com/v21.0/me/businesses",
            params={"fields": "id,name,verification_status", "access_token": user_access_token}
        ).json()

        if "data" not in business_accounts or not business_accounts["data"]:
            return Response({"error": "No Business Manager accounts found"}, status=404)

        business_id = business_accounts["data"][0]["id"]
        business_name = business_accounts["data"][0]["name"]

        # Optional: Get email
        whatsapp_accounts = requests.get(
            f"https://graph.facebook.com/v21.0/{business_id}/owned_whatsapp_business_accounts",
            params={"fields": "id,name,message_template_namespace", "access_token": user_access_token}
        ).json()

        if "data" not in whatsapp_accounts or not whatsapp_accounts["data"]:
            return Response({"error": "No WhatsApp Business accounts found"}, status=404)

        waba_id = whatsapp_accounts["data"][0]["id"]

        phone_data = requests.get(
            f"https://graph.facebook.com/v21.0/{waba_id}/phone_numbers",
            params={"fields": "id,display_phone_number,verified_name", "access_token": user_access_token}
        ).json()

        whatsapp_phone = None
        whatsapp_phone_id = None
        if "data" in phone_data and phone_data["data"]:
            whatsapp_phone = phone_data["data"][0].get("display_phone_number")
            whatsapp_phone_id = phone_data["data"][0].get("id")

        # ✅ Fetch business profile
        try:
            business_profile = BusinessProfile.objects.get(id=state)
        except BusinessProfile.DoesNotExist:
            return Response({"error": "Invalid BusinessProfile ID"}, status=404)

        # 5️⃣ Save or update in DB
        obj, created = BusinessWhatsappProfile.objects.update_or_create(
            business_profile=business_profile,
            defaults={
                "business_name": business_name,
                "manager_id": business_id,
                "whatsapp_account_id": waba_id,
                "whatsapp_phone": whatsapp_phone,
                # "collections": business_profile.collections,
                "authorize": True
            }
        )
        return redirect(f"https://app.einvotca.com/settings/whatsapp-integration?status=connected&id={str(obj.id)}")


class FinancialAccountListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        type = request.query_params.get('type')  # expense, income, supplier, customer, owner
        location = request.user.business_profile
        setting = AccountSetting.objects.filter(location=location).first()

        root = None
        if type == 'expense':
            root = setting.expense
        elif type == 'income':
            root = setting.income
        elif type == 'supplier':
            root = setting.payable_account
        elif type == 'customer':
            root = setting.receive_account
        elif type == 'owner_drawing':
            root = setting.equity
        elif type == 'employee':
            root = setting.expense
        elif type == 'investor':
            root = setting.equity

        if not root:
            return Response([])

        queryset = FinancialAccounts.objects.filter(location=location, parent__isnull=False).filter(
            Q(parent=root) | Q(parent__parent=root) | Q(parent__parent__parent=root)
        )

        serializer = FinancialAccountListSerializer(queryset, many=True)
        return Response(serializer.data)


class SupplierDetailListApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SupplierDetailsSerializer

    def get_queryset(self):
        return Suppliers.objects.by_location(self.request.user).filter(account_type="supplier")


class CustomerDetailListApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SupplierDetailsSerializer

    def get_queryset(self):
        return Customers.objects.by_location(self.request.user).filter(account_type="customer")


class CustomerSupplierPaymentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        type = request.query_params.get('type')
        ref_id = request.data.get('ref_id')
        location = request.user.business_profile
        setting = AccountSetting.objects.filter(location=location).first()
        party = Parties.objects.get(id=ref_id)

        root = None
        if type == 'supplier':
            root = setting.payable_account
        elif type == 'customer':
            root = setting.receive_account

        if not root:
            return Response([])

        return Response({
            "data": (FinancialAccountListSerializer(party.chart_of_account).data if party.chart_of_account else None)
        })


class EmployeeListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [HasEmployeesRoles]
    serializer_class = EmployeesSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'designation', 'email']

    def get_queryset(self):
        return Employees.objects.by_location(self.request.user).filter(deleted=False)

    def perform_create(self, serializer):
        employee = serializer.save(location=self.request.user.business_profile)
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Employees", action_type="create",
                                 description=f"Employee created {employee.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))


class EmployeeReportApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        employee = FinancialAccounts.objects.filter(employees__isnull=False).distinct()
        amount = JournalDetail.objects.filter(account__in=employee).aggregate(amount=Sum('amount'))['amount'] or 0
        employee_count = Employees.objects.by_location(self.request.user).filter(deleted=False).count()

        return Response({
            'amount': amount,
            'employee': employee_count
        }, status=200)


class EmployeeRetrieveUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasEmployeesRoles]
    serializer_class = EmployeesSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_field)
        return Employees.objects.by_location(self.request.user).filter(slug=slug)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        employee = self.get_object()
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Employees", action_type="update",
                                 description=f"Employee updated {employee.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response

    def destroy(self, request, *args, **kwargs):
        employee = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        activity_logs_task.delay(location_id=self.request.user.business_profile.id, user_id=self.request.user.id,
                                 module="Employees", action_type="delete",
                                 description=f"Employee Deleted {employee.name}",
                                 ip_address=self.request.META.get('REMOTE_ADDR'))
        return response


class CustomerSupplierApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSupplierSerializer

    def get_queryset(self):
        return Parties.objects.filter(location=self.request.user.business_profile).filter(
            account_type__in=['customer', 'supplier']).filter(deleted=False)


class ActivityLogsListApiView(generics.ListAPIView):
    permission_classes = [HasActivityLogsRoles]
    serializer_class = ActivityLogsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['user__username', 'location__registered_name', 'module', 'action_type']
    filterset_class = ActivityLogsFilter

    def get_queryset(self):
        return ActivityLog.objects.by_location(self.request.user).filter(deleted=False)


class WhatsAppIntegrationListCreateApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = self.request.data
        profile_data = slugify(self.request.user.business_profile.registered_name)

        url = f"{BOT_URL}/instance/create"
        headers = {
            "Content-Type": "application/json",
            "apikey": BOT_KEY
        }
        data_payload = {
            "instanceName": profile_data,
            "number": data['phone_number'],
            "integration": "WHATSAPP-BAILEYS",
            "qrcode": True
        }

        response = requests.post(url, headers=headers, json=data_payload)
        response_json = response.json()
        qr_code = response_json.get("qrcode")

        if str(response.status_code) == '201':

            BusinessWhatsappProfile.objects.get_or_create(
                business_profile=self.request.user.business_profile,
                defaults={
                    "instance_name": profile_data,
                    "authorize_key": response_json['hash']['apikey'],
                    "phone_number": data['phone_number'],
                    "admin_phone": data['admin_phone'],
                    "collections": self.request.user.collections,
                    "qrcode": True,
                }

            )

            return Response({'message': qr_code}, response.status_code)
        else:
            return Response({'message': response_json['response']['message'][0]}, response.status_code)


class ConnectInstanceApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        instance = BusinessWhatsappProfile.objects.filter(business_profile=self.request.user.business_profile).first()
        url = f"{BOT_URL}/instance/connect/{instance.instance_name}"
        headers = {
            "Content-Type": "application/json",
            "apikey": BOT_KEY
        }
        response = requests.get(url, headers=headers)
        response_json = response.json()
        if str(response.status_code) == '200':
            return Response(response_json, response.status_code)
        else:
            return Response({'message': response_json['response']['message'][0]}, response.status_code)


class ConnectStatusApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        instance = BusinessWhatsappProfile.objects.filter(business_profile=self.request.user.business_profile).first()
        url = f"{BOT_URL}/instance/connectionState/{instance.instance_name}"
        headers = {
            "Content-Type": "application/json",
            "apikey": BOT_KEY
        }
        response = requests.get(url, headers=headers)
        response_json = response.json()
        if str(response.status_code) == '200':
            return Response(response_json, response.status_code)
        else:
            return Response({'message': response_json['response']['message'][0]}, response.status_code)


class GetWhatsappProfileApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = BusinessWhatsappProfile.objects.filter(business_profile=request.user.business_profile).first()

        if profile:
            url = f"{BOT_URL}/instance/connectionState/{profile.instance_name}"
            headers = {
                "Content-Type": "application/json",
                "apikey": BOT_KEY
            }
            try:
                response = requests.get(url, headers=headers, timeout=10)
                print(response.json())
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                profile_data = BusinessWhatsappProfile.objects.filter(
                    business_profile=request.user.business_profile).first()
                if profile_data:
                    profile_data.delete()
                    return Response({"step": 1, "message": f"Profile deleted because instance check failed for {url}"},
                                    status=500)
                else:
                    return Response({"step": 1, "message": f"Instance not created for {url}"}, status=500)

            response_json = response.json()
            status_state = response_json.get("instance", {}).get("state", "").lower()

            if status_state in ["open", "connected"]:

                content = (
                    f"{profile.instance_name} phone number is {profile.phone_number}"

                )

                doc = {
                    "id": str(profile.id),
                    "content": content,
                    "metadata": {
                        "apikey": profile.authorize_key,
                        "phone_number": str(profile.phone_number),
                        "admin_phone": profile.admin_phone,
                        "collections": profile.collections,
                        "instance_name": profile.instance_name
                    }
                }

                profile.authorize = True
                profile.data_collection = doc
                profile.save()
                url = f"{BOT_URL}/webhook/set/{profile.instance_name}"
                payload = {
                    "url": f"{WEB_HOOK_URL}/?verify_token={VERIFY_TOKEN}",
                    "webhook_by_events": False,
                    "webhook_base64": False,
                    "events": ['MESSAGES_UPSERT']
                }
                headers = {
                    "Content-Type": "application/json",
                    "apikey": BOT_KEY
                }
                response = requests.post(url, json=payload, headers=headers)
                return Response({"step": 3, "message": "Instance connected", "number": profile.phone_number},
                                status=200)

            elif status_state in ["connecting", "close", "disconnected"]:
                return Response({"step": 2, "message": f"Instance state: {status_state}"}, status=200)

        elif not profile:
            return Response({"step": 1, "message": "No instance created yet"}, status=200)

        elif not profile.authorize:
            return Response({"step": 2, "message": profile.instance_name}, status=200)


class SetWebHookApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        instance = BusinessWhatsappProfile.objects.filter(business_profile=self.request.user.business_profile).first()
        url = f"{BOT_URL}/webhook/set/{instance.instance_name}"

        payload = {
            "url": f"{WEB_HOOK_URL}/?verify_token={VERIFY_TOKEN}",
            "webhook_by_events": True,
            "webhook_base64": False,
            "events": ['MESSAGES_UPSERT']
        }
        headers = {
            "Content-Type": "application/json",
            "apikey": BOT_KEY
        }
        response = requests.post(url, json=payload, headers=headers)
        response_json = response.json()
        print(response_json)
        if response.status_code == 201:
            return Response({"message": "Webhook set successfully"}, status=200)
        else:
            return Response({"message": "Failed to set webhook"}, status=500)


class LogoutWhatsappProfileApiView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        instance = BusinessWhatsappProfile.objects.filter(business_profile=request.user.business_profile).first()

        if not instance:
            return Response({"step": 1, "message": "No WhatsApp instance found to logout"}, status=404)

        url = f"{BOT_URL}/instance/delete/{instance.instance_name}"
        headers = {
            "apikey": BOT_KEY
        }

        try:
            response = requests.delete(url, headers=headers, timeout=10)
            response.raise_for_status()
            response_json = response.json()
            instance.delete()

            return Response({"message": "Logout successful", "data": response_json}, status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response({"message": f"Failed to logout instance: {str(e)}"}, status=500)


class ContactImportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ContactImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        connection = get_object_or_404(BusinessWhatsappProfile, business_profile=self.request.user.business_profile)
        file = serializer.validated_data['file']

        if file.name.endswith(".csv"):
            import_contacts_from_csv(file, request.user.business_profile, connection)
        elif file.name.endswith(".vcf"):
            import_contacts_from_vcf(file, request.user.business_profile, connection)
        else:
            return Response({"error": "Unsupported file format. Use CSV or VCF."},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Contacts imported successfully ✅"}, status=status.HTTP_201_CREATED)


class WhatsAppContactCreateApiView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WhatsAppContactsSerializer

    def get_queryset(self):
        return WhatsappContacts.objects.filter(location=self.request.user.business_profile)

    def perform_create(self, serializer):
        serializer.save(location=self.request.user.business_profile)


class WhatsAppContactUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WhatsAppContactsSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return WhatsappContacts.objects.filter(location=self.request.user.business_profile)


class SendMessageContactsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        msg_type = request.data.get('type')
        contacts_ids = request.data.get('contacts', [])
        instance = get_object_or_404(BusinessWhatsappProfile, business_profile=self.request.user.business_profile)

        contacts = WhatsappContacts.objects.filter(id__in=contacts_ids, user=request.user)
        results = []

        for contact in contacts:
            number = contact.number

            try:
                if msg_type == "text":
                    data = send_text_message(instance, number, request.data.get("text"))
                elif msg_type == "media":
                    media_url = request.data.get("media")
                    media_type, file_name = get_media_info(media_url)
                    data = send_media_message(
                        instance, number,
                        media_type,
                        file_name,
                        request.data.get("caption"),
                        media_url,
                    )
                elif msg_type == "audio":
                    data = send_audio_message(instance, number, request.data.get("audio"))
                else:
                    results.append({"error": "Invalid type"})
                    continue

                results.append(data.json())
            except Exception as e:
                results.append({"error": str(e)})

        return Response({"message": "Messages processed", "results": results})
