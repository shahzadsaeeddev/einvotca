from django.db.models.aggregates import Sum
from transactions.models import JournalDetail


class PartiesBalanceMixins:

    def get_balance(self, obj):
        account = obj.chart_of_account
        if not account:
            return 0
        entries = JournalDetail.objects.filter(account=account)
        total = entries.aggregate(balance=Sum('amount'))['balance'] or 0
        return round(total, 2)


class FinancialAccountMixins:

    def get_balance(self, obj):
        journal_detail = JournalDetail.objects.filter(account_id=obj.id).aggregate(amount=Sum('amount'))['amount'] or 0

        return journal_detail


class BankAccountMixins:

    def get_balance(self, obj):
        journal_detail = \
            JournalDetail.objects.filter(account_id=obj.chart_of_account.id, location=obj.location).aggregate(
                amount=Sum('amount'))['amount'] or 0

        return journal_detail