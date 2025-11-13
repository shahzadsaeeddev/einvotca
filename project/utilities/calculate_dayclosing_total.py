from datetime import date

from django.db.models.aggregates import Sum
from django.db.models.query_utils import Q

from transactions.models import JournalLine, DayClosing


def calculate_day_closing_totals(user, location):
    today = date.today()

    existing_closing = DayClosing.objects.filter(user=user, location=location, created_at__date=today).first()

    if existing_closing:
        return {
            "sales": 0.00,
            "discount": 0.00,
            "returns": 0.00,
            "opening_balance": float(existing_closing.opening_balance),
            "closing_balance": 0.00,
            "closing_date": existing_closing.created_at,
            "payment_method": [],
        }

    journal_lines = JournalLine.objects.filter(created_by=user, location=location, date_time__date=today,
                                               transaction_type__in=['SALE', 'CREDIT_NOTE'])

    sales_total = journal_lines.filter(is_return=False).aggregate(total=Sum('paid_amount'))['total'] or 0
    discount_total = journal_lines.filter(is_return=False).aggregate(total=Sum('discount'))['total'] or 0
    returns_total = journal_lines.filter(Q(is_return=True) | Q(returned_amount__gt=0)).aggregate(
        total=Sum('paid_amount'))['total'] or 0

    payment_method = journal_lines.values('payment_method__name').annotate(
        total_paid=Sum('paid_amount')).order_by('payment_method__name')

    last_closing = DayClosing.objects.filter(user=user, location=location).order_by('-created_at').first()
    opening_balance = last_closing.closing_balance if last_closing else 0
    closing_balance = sales_total - discount_total - returns_total

    return {
        "sales": round(sales_total, 2),
        "discount": round(discount_total, 2),
        "returns": round(returns_total, 2),
        "opening_balance": round(opening_balance, 2),
        "closing_balance": round(closing_balance, 2),
        "closing_date": None,
        "payment_method": payment_method,
    }
