import json, calendar
import SalesEstimates.models as m
from django.http import HttpResponse
from django.db import models as db_models

def customer_json(request):
    customers = m.Customer.objects.all().values_list('id', 'name')
    sales_periods = m.SalesPeriod.objects.all().order_by('start_date').values_list('id', 'start_date')
    result = []
    for cid, name in customers:
#         all_sales = m.SKUSales.objects.filter(csku__customer__id=cid).values_list('period__period__start_date', 'income')
        sales = []
        for sp in sales_periods:
            sales.append((date2unix(sp[1]), get_income(sp[0], cid)))
        result.append({'key': name, 'values': sales})
    return HttpResponse(json.dumps(result), mimetype = 'application/json')

def get_income(sp_id, cid):
    sku_sales = m.SKUSales.objects.filter(period__period__id = sp_id, csku__customer__id=cid)
    income = sku_sales.aggregate(income = db_models.Sum('income'))['income']#skus_sold = db_models.Sum('sales'), 
    if income is None:
        return 0
    return float(income)


def date2unix(date):
        return calendar.timegm(date.timetuple())*1000