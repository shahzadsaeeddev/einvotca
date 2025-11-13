
def create_financial_accounts(location):
    from .models import FinancialAccounts

    type_prefixes = {
        "asset": "AS",
        "liability": "LI",
        "equity": "EQ",
        "income": "IN",
        "expense": "EX",
        "cgs": "CG",
        "bank": "BK",
        "current_asset": "CA",
    }

    type_mapping = {
        "asset": "Asset",
        "liability": "Liability",
        "equity": "Equity",
        "income": "Revenue",
        "expense": "Expense",
        "cgs": "CGS",
        "bank": "Asset",
        "current_asset": "Asset"
    }

    # First create the main parent accounts (Asset, Liability, Equity, etc.)
    master_accounts = {}
    main_types = ["asset", "liability", "equity", "income", "expense", "cgs"]

    for type_key in main_types:
        title = type_mapping[type_key]
        prefix = type_prefixes[type_key]
        code = f"{prefix}-0000"
        is_ordinary = type_key in ["income", "expense", "cgs"]
        try:
            acc = FinancialAccounts.objects.create(
                code=code,
                title=title,
                type=title,
                parent=None,
                location=location,
                is_ordinary=is_ordinary
            )
            master_accounts[type_key] = acc
        except Exception as e:
            print(f"Error creating main account '{title}': {e}")

    sub_groups = {
        "bank": {
            "title": "Bank",
            "prefix": "BK",
            "parent": "asset"
        },
        "current_asset": {
            "title": "Current Asset",
            "prefix": "CA",
            "parent": "asset"
        }
    }

    for group_key, group_data in sub_groups.items():
        code = f"{group_data['prefix']}-0000"
        try:
            acc = FinancialAccounts.objects.create(
                code=code,
                title=group_data['title'],
                type=type_mapping[group_key],
                parent=master_accounts[group_data['parent']],
                location=location,
                is_ordinary=False
            )
            master_accounts[group_key] = acc
        except Exception as e:
            print(f"Error creating {group_data['title']} account: {e}")

    chart_of_accounts = [
        # Current Assets (under Current Asset group)
        {"name": "Cash", "type": "current_asset"},
        {"name": "Petty Cash", "type": "current_asset"},

        # Other Assets
        {"name": "Accounts Receivable (A/R)", "type": "asset"},
        {"name": "Inventory", "type": "asset"},
        {"name": "Investments", "type": "asset"},

        # Liabilities
        {"name": "Accounts Payable (A/P)", "type": "liability"},
        {"name": "Credit Card Payables", "type": "liability"},
        {"name": "Tax", "type": "liability"},



        # Equity
        {"name": "Owner's Equity", "type": "equity"},
        {"name": "Retained Earnings", "type": "equity"},
        {"name": "Common Stock", "type": "equity"},
        {"name": "Additional Paid-in Capital", "type": "equity"},
        {"name": "Opening Balance Equity", "type": "equity"},
        {"name": "Profit & Loss", "type": "equity"},

        # Income (all will have is_ordinary=True)
        {"name": "Sales Revenue", "type": "income"},
        {"name": "Service Revenue", "type": "income"},
        {"name": "Interest Income", "type": "income"},
        {"name": "Rental Income", "type": "income"},

        # CGS (all will have is_ordinary=True)
        {"name": "Cost of Goods Sold (COGS)", "type": "cgs"},
        {"name": "Opening Balance", "type": "cgs"},
        {"name": "Closing Balance", "type": "cgs"},

        # Expenses (all will have is_ordinary=True)
        {"name": "Rent Expense", "type": "expense"},
        {"name": "Salaries & Wages", "type": "expense"},
        {"name": "Utilities", "type": "expense"},
        {"name": "Office Supplies", "type": "expense"},
        {"name": "Bank Fees", "type": "expense"},
        {"name": "Payroll Liabilities", "type": "expense"},
    ]

    prefix_counters = {key: 0 for key in type_prefixes.keys()}
    created = 0

    for acc in chart_of_accounts:
        acc_type_key = acc["type"]
        prefix = type_prefixes.get(acc_type_key, acc_type_key[:2].upper())
        prefix_counters[acc_type_key] += 1
        number = prefix_counters[acc_type_key]
        code = f"{prefix}-{number:04d}"

        is_ordinary = acc_type_key in ["income", "expense", "cgs"]

        try:
            fa = FinancialAccounts.objects.create(
                code=code,
                title=acc["name"],
                type=type_mapping[acc_type_key],
                parent=master_accounts[acc_type_key],
                location=location,
                is_ordinary=is_ordinary
            )
            created += 1
        except Exception as e:
            print(f"Error creating {acc['name']}: {e}")

    print(f"✅ Total child accounts created: {created}")