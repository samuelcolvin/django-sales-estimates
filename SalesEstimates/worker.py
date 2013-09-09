import settings
from datetime import datetime as dtdt
from datetime import timedelta as td

import SalesEstimates.models as m
from django.db import models as db_models
import inspect, operator

def generate_sales_periods(log):
    start_date = dtdt.strptime(settings.SALES_PERIOD_START_DATE, settings.CUSTOM_DATE_FORMAT)
    system_finish_date = dtdt.strptime(settings.SALES_PERIOD_FINISH_DATE, settings.CUSTOM_DATE_FORMAT)
    months = settings.SALES_PERIOD_LENGTH
    periods = []
    
    while start_date < system_finish_date:
        next_start_month = start_date.month + months
        next_start_date = start_date
        if next_start_month > 12:
            next_start_month = next_start_month % 12
            next_start_date = next_start_date.replace(year = start_date.year + 1)
        next_start_date = next_start_date.replace(month = next_start_month)
        finish_date = next_start_date - td(days=1)
        periods.append({'start': start_date, 'finish': finish_date})
        start_date = next_start_date
        
    log('\nadding periods to db...')
    for period in periods:
        existing = m.SalesPeriod.objects.filter(start_date = period['start'], finish_date = period['finish'])
        if existing.count() == 0:
            sp = m.SalesPeriod.objects.create(start_date = period['start'], finish_date = period['finish'])
            sp.xl_id = sp.id
            sp.save()
    log('created %d sales periods' % m.SalesPeriod.objects.count())
        
def populate_sales_periods(log):
    log('Creating customer sales periods and SKU sales periods...')
    for period in m.SalesPeriod.objects.all():
        for customer in m.Customer.objects.all():
            csp = m.CustomerSalesPeriod.objects.filter(customer=customer, period=period)
            if csp.count() > 0:
                csp = csp[0]
            else:
                csp = m.CustomerSalesPeriod.objects.create(customer=customer, period=period)
            for csku in customer.c_skus.all():
                existing = m.SKUSales.objects.filter(period=csp, csku=csku)
                if existing.count() == 0:
                    m.SKUSales.objects.create(period=csp, csku=csku)
    log('Created %d customer sales periods and %s sku sales periods' % 
        (m.CustomerSalesPeriod.objects.count(), m.SKUSales.objects.count()))

def generate_auto_sales_figures(log):
    sku_count = 0
    for csp in m.CustomerSalesPeriod.objects.all():
        for csku in m.CustomerSKU.objects.all():
            sku_sales = m.SKUSales(period=csp, csku=csku)
            if csp.store_count != None and csku.sale_rate != None:
                sku_sales.sales = csp.store_count * csku.sale_rate * settings.SALES_PERIOD_LENGTH * 4
            sku_sales.save()
            sku_count += 1
    log('%d SKU sale quantities calculated' % sku_count)
        

def clear_se(log):
    for mod_name in dir(m):
        if mod_name == 'User':
            continue
        mod = getattr(m, mod_name)
        if inspect.isclass(mod)  and issubclass(mod, db_models.Model) and not mod._meta.abstract:
            mod.objects.all().delete()
            log('Deleting all records from %s' % mod.__name__)
            
def calc_totle_sales(sku_sales_group):
    return sku_sales_group.aggregate(total_sales = db_models.Sum('sales'))['total_sales']

def calc_sku_sale_income(sku_sales_group):
    sales = map(float, sku_sales_group.values_list('sales', flat=True))
    prices = map(float, sku_sales_group.values_list('csku__price', flat=True))
    return sum(map(operator.mul, sales, prices))

def calc_sku_sale_group_cost(sku_sales_group):
    cost = 0
    sp = sku_sales_group[0].period.period
    for sku_sales in sku_sales_group:
        for comp in m.Component.objects.filter(assemblies__skus__c_skus__sku_sales=sku_sales):
            sku_sales_group = m.SKUSales.objects.filter(period__period=sp).filter(csku__sku__assemblies__components__order_group=comp.order_group)
            orders = calc_totle_sales(sku_sales_group)
            cost += comp.order_group.cost(orders)*orders
    return cost



