
from rest_framework.permissions import BasePermission
from .models import Users


class HasRolesManager(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        return request.user.is_manager



class HasProductsRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_items
        elif request.method in ['PUT', 'PATCH']:
            return request.user.can_update_items
        elif request.method == 'DELETE':
            return request.user.can_delete_items
        elif request.method == 'GET':
            return request.user.can_view_items
        return False


class HasProductsAttributesRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_items_attribute
        elif request.method == 'GET':
            return request.user.can_view_items_attribute
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.can_manage_items_attribute
        return False


class HasSaleInvoiceRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_view_sales
        elif request.method == 'GET':
            return request.user.can_create_sales
        return False


class HasDayClosingRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_day_closing
        elif request.method == 'GET':
            return request.user.can_view_day_closing
        return False


class HasCreditNoteRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_credit_notes or request.user.can_approve_credit_note
        elif request.method == 'GET':
            return request.user.can_view_credit_notes
        return False


class HasPurchaseInvoiceRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_purchases
        elif request.method == 'GET':
            return request.user.can_view_purchases
        return False


class HasDebitNoteRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_debit_notes
        elif request.method == 'GET':
            return request.user.can_view_debit_notes
        elif request.method == 'POST':
            return request.user.can_approve_debit_notes
        return False


class HasPaymentVoucherRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_payment_voucher
        elif request.method == 'GET':
            return request.user.can_view_payment_voucher
        return False


class HasReceiptVoucherRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        method = request.method

        if method == 'GET':
            return request.user.can_view_receipt_voucher
        elif method == 'POST':
            return request.user.can_create_receipt_voucher or request.user.can_approve_receipt_voucher
        return False


class HasCustomersRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_customers
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.can_manage_customers
        elif request.method == 'GET':
            return request.user.can_view_customers
        return False


class HasSuppliersRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_suppliers
        elif request.method == 'GET':
            return request.user.can_view_suppliers
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.can_manage_suppliers

        return False


class HasInvestorsRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_investors
        elif request.method == 'GET':
            return request.user.can_view_investors
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.can_manage_investors

        return False


class HasBankAccountsRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_banks
        elif request.method == 'GET':
            return request.user.can_view_banks
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.can_manage_banks

        return False


class HasFinancialAccountsRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_financial_accounts
        elif request.method == 'GET':
            return request.user.can_view_financial_accounts
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.can_manage_financial_accounts

        return False


class HasEmployeesRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_employees
        elif request.method == 'GET':
            return request.user.can_view_employees
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.can_manage_employees

        return False


class HasIncomeExpenseRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_income_expense
        elif request.method == 'GET':
            return request.user.can_view_income_expense
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.can_manage_income_expense

        return False


class HasAssetLiabilityRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_liability
        elif request.method == 'GET':
            return request.user.can_view_liability
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.can_manage_liability

        return False


class HasInventoryReportRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.can_view_inventory_report
        return False


class HasStockAdjustmentReportRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.can_view_stock_adjustment
        return False



class HasOutStockReportRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.can_view_out_stock_report
        return False


class HasActivityLogsRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.can_view_activity_logs
        return False



class HasGeneralJournalReportRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.can_view_general_journal
        return False



class HasLegerReportRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.can_view_leger_report
        return False


class HasTrailBalanceReportRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.trail_balance_report
        return False


class HasIncomeStatementReportRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.can_view_income_statement_report
        return False


class HasBalanceSheetReportRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.can_view_balance_sheet
        return False


class HasSaleReportRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.can_view_sale_report
        return False


class HasPurchaseReportRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.can_view_purchase_report
        return False


class HasBusinessProfileRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.can_view_business_profile
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.can_manage_business_profile

        return False


class HasInvoiceSetupRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_invoice_setup
        elif request.method == 'GET':
            return request.user.can_view_invoice_setup
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.can_manage_invoice_setup

        return False



class HasUserAccountsRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_users
        elif request.method == 'GET':
            return request.user.can_view_users
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.can_manage_users

        return False



class HasDiningTableRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.can_create_dining
        elif request.method == 'GET':
            return request.user.can_view_dining
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.can_manage_dining

        return False


class HasAccountSettingRoles(BasePermission):
    """
    Check if the user has any of the required AMP Roles
    """

    message = (
        "You do not have any Assets Management Roles, "
        "Please contact Keycloak Administrator to add roles into your Keycloak Account"
    )

    def has_permission(self, request, view):
        if request.method in ['GET', 'PATCH']:
            return request.user.can_view_account_settings

        return False






