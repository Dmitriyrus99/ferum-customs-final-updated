def calculate_total_payable(doc, method):
    doc.total_payable = sum([row.amount for row in doc.pay_items or []])
