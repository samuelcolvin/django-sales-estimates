import _utils, settings

def update_csp(customer_id, existing):
    mysql, msgs = _utils.get_con()
    if existing:
        msgs += mysql.update_customer_csp(customer_id)
    else:
        msgs += mysql.add_customer_csp(customer_id)
    print msgs

def caculate_sales():
    msgs = _utils.generate_skusales()
    print msgs