def total_price(items, tax_rate=0.1):
    subtotal = sum(i["price"] * i["qty"] for i in items)
    return subtotal * (1 + tax_rate)
