CSID = {
    "sandbox": "https://gw-fatoora.zatca.gov.sa/e-invoicing/developer-portal/compliance",
    "simulation": "https://gw-fatoora.zatca.gov.sa/e-invoicing/simulation/compliance",
    "production": "https://gw-fatoora.zatca.gov.sa/e-invoicing/core/compliance",
}

X509 = {
    "sandbox": "https://gw-fatoora.zatca.gov.sa/e-invoicing/developer-portal/production/csids",
    "simulation": "https://gw-fatoora.zatca.gov.sa/e-invoicing/simulation/production/csids",
    "production": "https://gw-fatoora.zatca.gov.sa/e-invoicing/core/production/csids",
}

COMPLIANCE_URL = {
    "sandbox": "https://gw-fatoora.zatca.gov.sa/e-invoicing/developer-portal/compliance/invoices",
    "simulation": "https://gw-fatoora.zatca.gov.sa/e-invoicing/simulation/compliance/invoices",
    "production": "https://gw-fatoora.zatca.gov.sa/e-invoicing/core/compliance/invoices",
}

REPORTING_URL = {
    "sandbox": 'https://gw-fatoora.zatca.gov.sa/e-invoicing/developer-portal/invoices/reporting/single',
    "simulation": 'https://gw-fatoora.zatca.gov.sa/e-invoicing/simulation/invoices/reporting/single',
    "production": 'https://gw-fatoora.zatca.gov.sa/e-invoicing/core/invoices/reporting/single',
}

CLEARANCE_URL = {
    "sandbox": 'https://gw-fatoora.zatca.gov.sa/e-invoicing/developer-portal/invoices/clearance/single',
    "simulation": 'https://gw-fatoora.zatca.gov.sa/e-invoicing/simulation/invoices/clearance/single',
    "production": "https://gw-fatoora.zatca.gov.sa/e-invoicing/core/invoices/clearance/single'"
}

INVOICE_CODES = {
    "simplified": {
        "invoice": "<cbc:InvoiceTypeCode name='0200000'>388</cbc:InvoiceTypeCode>",
        "debit_note": "<cbc:InvoiceTypeCode name='0211010'>381</cbc:InvoiceTypeCode>",
        "credit_note": "<cbc:InvoiceTypeCode name='0211010'>383</cbc:InvoiceTypeCode>",
        "prepayment":"<cbc:InvoiceTypeCode name='0200000'>386</cbc:InvoiceTypeCode>",
    },
    "standard": {
        "invoice": "<cbc:InvoiceTypeCode name='0100000'>388</cbc:InvoiceTypeCode>",
        "debit_note": "<cbc:InvoiceTypeCode name='0100000'>383</cbc:InvoiceTypeCode>",
        "credit_note": "<cbc:InvoiceTypeCode name='0100000'>381</cbc:InvoiceTypeCode>",
        "prepayment":"<cbc:InvoiceTypeCode name='0100000'>386</cbc:InvoiceTypeCode>",
    }
}
