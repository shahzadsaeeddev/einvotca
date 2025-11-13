from neksio_api.models import AccountSetting, FinancialAccounts
from .models import JournalDetail


class Transaction:

    def __init__(self, business_id, master):
        self.id = business_id
        self.master = master
        self.account = self._get_account_setting()

    def _get_account_setting(self):
        account = AccountSetting.objects.filter(location_id=self.id).first()
        if not account:
            raise ValueError(f"Invalid account with ID: {self.id}")
        return account

    def purchase(self):
        location = self.id
        inventory = self.account.inventory
        supplier = self.master.party.chart_of_account
        tax = self.account.tax

        if self.master and self.master.payment_method:
            payment_method = self.master.payment_method.chart_of_account
        else:
            payment_method = None

        # debit single entry
        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=inventory,
                                     amount=self.master.payable_amount - self.master.tax_amount,
                                     account_title=supplier.title)
        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=tax,
                                     amount=self.master.tax_amount, account_title=supplier.title)
        # credit
        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=supplier.id,
                                     amount=-abs(self.master.payable_amount), account_title=supplier.title)

        if self.master.paid_amount > 0:
            # Debit double entry
            JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=supplier.id,
                                         amount=self.master.paid_amount, account_title=supplier.title)
            # Credit
            JournalDetail.objects.create(location_id=location, transaction_id=self.master.id,
                                         account_id=payment_method.id,
                                         amount=-abs(self.master.paid_amount), account_title=supplier.title)

    def debit_note(self):
        location = self.id
        inventory = self.account.inventory
        supplier = self.master.party.chart_of_account
        tax = self.account.tax

        if self.master and self.master.payment_method:
            payment_method = self.master.payment_method.chart_of_account
        else:
            payment_method = None

        # credit single entry
        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=inventory,
                                     amount=-abs(self.master.payable_amount - self.master.tax_amount),
                                     account_title=supplier.title)
        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=tax,
                                     amount=-abs(self.master.tax_amount), account_title=supplier.title)
        # debit
        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=supplier.id,
                                     amount=self.master.payable_amount, account_title=supplier.title)

        if self.master.paid_amount > 0:
            # Debit
            JournalDetail.objects.create(location_id=location, transaction_id=self.master.id,
                                         account_id=payment_method.id,
                                         amount=self.master.paid_amount, account_title=supplier.title)

            # credit double entry
            JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=supplier.id,
                                         amount=-abs(self.master.paid_amount), account_title=supplier.title)



    def sale(self):
        location = self.id
        inventory = self.account.inventory
        customer = self.master.party.chart_of_account
        tax = self.account.tax
        cgs = self.account.csg
        sales = self.account.sales

        print("CARRIAGE SOURCE" , self.master.carriage_source)

        if self.master and self.master.payment_method:
            payment_method = self.master.payment_method.chart_of_account
        else:
            payment_method = None

        # debit single entry
        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=sales,
                                     amount=-abs(self.master.payable_amount - self.master.tax_amount),
                                     account_title=customer.title)

        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=tax,
                                     amount=-abs(self.master.tax_amount), account_title=customer.title)
        # credit
        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=customer.id,
                                     amount=self.master.payable_amount, account_title=customer.title)

        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=inventory,
                                     amount=-abs(self.master.cost_amount), account_title=customer.title)

        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=cgs,
                                     amount=self.master.cost_amount, account_title=customer.title)

        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id,
                                     account_id=self.master.carriage_source,
                                     amount=-abs(self.master.carriage_amount), account_title=customer.title)

        if self.master.paid_amount > 0:
            # Debit double entry
            JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=customer.id,
                                         amount=-abs(self.master.paid_amount), account_title=customer.title)
            # Credit
            JournalDetail.objects.create(location_id=location, transaction_id=self.master.id,
                                         account_id=payment_method.id,
                                         amount=self.master.paid_amount, account_title=customer.title)

    def credit_note(self):
        location = self.id
        inventory = self.account.inventory
        customer = self.master.party.chart_of_account
        tax = self.account.tax
        cgs = self.account.csg
        sales = self.account.sales

        if self.master and self.master.payment_method:
            payment_method = self.master.payment_method.chart_of_account
        else:
            payment_method = None

        # debit single entry
        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=inventory,
                                     amount=self.master.payable_amount - self.master.tax_amount,
                                     account_title=customer.title)
        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=tax,
                                     amount=self.master.tax_amount, account_title=customer.title)
        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=customer.id,
                                     amount=-abs(self.master.payable_amount), account_title=customer.title)

        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=sales,
                                     amount=self.master.payable_amount, account_title=customer.title)
        JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=cgs,
                                     amount=-abs(self.master.payable_amount), account_title=customer.title)

        if self.master.paid_amount > 0:
            JournalDetail.objects.create(location_id=location, transaction_id=self.master.id, account_id=customer.id,
                                         amount=self.master.paid_amount, account_title=customer.title)

            JournalDetail.objects.create(location_id=location, transaction_id=self.master.id,
                                         account_id=payment_method.id,
                                         amount=-abs(self.master.paid_amount), account_title=customer.title)
