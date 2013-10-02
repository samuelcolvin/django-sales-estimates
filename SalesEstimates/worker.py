import settings
from datetime import datetime as dtdt
from datetime import timedelta as td

import SalesEstimates.models as m
from django.db import models as db_models
import inspect, operator

import SkeletalDisplay
import SkeletalDisplay.views_base as viewb
import decimal
from django.db import transaction
import time

from django.shortcuts import render

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
    xl_id = m.SalesPeriod.objects.all().aggregate(min_xlid = db_models.Min('xl_id'))['min_xlid']
    if xl_id is None:
        xl_id = 1
    else:
        xl_id += 1 
    sp_to_add = []
    for period in periods:
        existing = m.SalesPeriod.objects.filter(start_date = period['start'], finish_date = period['finish'])
        if existing.count() == 0:
            sp = m.SalesPeriod(start_date = period['start'], finish_date = period['finish'])
            sp.xl_id = xl_id
            xl_id += 1
            sp_to_add.append(sp)
    m.SalesPeriod.objects.bulk_create(sp_to_add)
    log('created %d sales periods' % m.SalesPeriod.objects.count())
    
def generate_customer_sp(log):
    t = time.time()
    existing = m.CustomerSalesPeriod.objects.all()
    log('deleting %d existing Customer Sales Periods' % existing.count())
    existing.delete()
    added = 0
    for customer in m.Customer.objects.all().iterator():
        for sp in m.SalesPeriod.objects.all().iterator():
            m.CustomerSalesPeriod.objects.create(customer = customer, period = sp)
            added +=1
    diff_mid = time.time() - t
    log('generated %d Customer Sales Periods in %0.3f secs' % (added, diff_mid))
    
def generate_cskui(log):
    log('%d exists CustomerSKUInfo groups' % m.CustomerSKUInfo.objects.count())
    t = time.time()
    log('Generating Customer SKU Information...')
    added = 0
    for customer in m.Customer.objects.all().iterator():
        for sku in customer.skus.all().iterator():
            already = m.CustomerSKUInfo.objects.filter(sku=sku, customer=customer)
            if not already.exists():
                m.CustomerSKUInfo.objects.create(sku=sku, customer=customer)
                added += 1
    diff_mid = time.time() - t
    log('generated %d CustomerSKUInfo groups in %0.3f secs' % (added, diff_mid))

def generate_auto_sales_figures(log):
    t = time.time()
    m.SKUSales.objects.all().delete()
    log('deleted all existing SKU sales estimates')
    sku_count = 0
    decimal.getcontext().prec = 4
    sku_sales_toadd = []
    for csp in m.CustomerSalesPeriod.objects.all().iterator():
        for csku in m.CustomerSKUInfo.objects.filter(customer=csp.customer).iterator():
            if csp.store_count != None and csku.sale_rate_factor != None:
                sku_sales = m.SKUSales(period=csp, csku=csku)
                sku_count += 1
                sku_sales.sales = csp.store_count * csku.sale_rate_factor * settings.SALES_PERIOD_LENGTH * 4
                sku_sales.income = decimal.Decimal(sku_sales.sales) * sku_sales.csku.price
                sku_sales_toadd.append(sku_sales)
    m.SKUSales.objects.bulk_create(sku_sales_toadd)
    log('%d SKU sale estimates added' % sku_count)
    mid = time.time()
    diff_mid = mid - t
    log('time taken to create SKUSales: %0.3f' % diff_mid)
    all_order_groups = m.OrderGroup.objects.all()
    with transaction.commit_on_success():
        for period in m.SalesPeriod.objects.all().iterator():
            order_group_costs = {}
            for order_group in all_order_groups:
                sku_sales_group_period = m.SKUSales.objects.filter(period__period=period).filter(csku__sku__assemblies__components__order_group=order_group).distinct()
                orders = calc_total_sales(sku_sales_group_period)
                cost = 0
                if orders is not None:
                    cost = order_group.cost(orders)
                order_group_costs[order_group.pk] = cost
            for sku_sales in m.SKUSales.objects.filter(period__period = period).iterator():
                order_groups = m.Component.objects.filter(order_group__components__assemblies__skus__c_skus__sku_sales = sku_sales).distinct().values_list('order_group__pk',flat=True)
                sku_sales.cost = sum([order_group_costs[og] for og in order_groups])*decimal.Decimal(sku_sales.sales)
                sku_sales.save()
    diff = time.time() - t
    diff_mid = diff - diff_mid
    log('time taken to calculate costs: %0.3f' % diff_mid)
    log('total time taken: %0.3f' % diff)
        

def clear_se(log):
    for mod_name in dir(m):
        if mod_name == 'User':
            continue
        mod = getattr(m, mod_name)
        if inspect.isclass(mod)  and issubclass(mod, db_models.Model) and not mod._meta.abstract:
            mod.objects.all().delete()
            log('Deleting all records from %s' % mod.__name__)
            
def delete_before_upload(log):
    clear_se(log)
    generate_sales_periods(log)
            
def calc_total_sales(sku_sales_group):
    return sku_sales_group.aggregate(total_sales = db_models.Sum('sales'))['total_sales']

# def calc_sku_sale_income(sku_sales_group):
#     sales = map(float, sku_sales_group.values_list('sales', flat=True))
#     prices = map(float, sku_sales_group.values_list('csku__price', flat=True))
#     return sum(map(operator.mul, sales, prices))
# 
# def calc_sku_sale_group_cost(sku_sales_group):
#     cost = 0
#     sp = sku_sales_group[0].period.period
#     for sku_sales in sku_sales_group:
#         for comp in m.Component.objects.filter(assemblies__skus__c_skus__sku_sales=sku_sales):
#             sku_sales_group_period = m.SKUSales.objects.filter(period__period=sp).filter(csku__sku__assemblies__components__order_group=comp.order_group)
#             orders = calc_total_sales(sku_sales_group_period)
#             cost += comp.order_group.cost(orders)*orders
#     return cost

def calc_sku_sales_cost(sku_sales):
    cost = 0
    sp = sku_sales.period.period
    for comp in m.Component.objects.filter(assemblies__skus__c_skus__sku_sales=sku_sales).iterator():
        sku_sales_group_period = m.SKUSales.objects.filter(period__period=sp).filter(csku__sku__assemblies__components__order_group=comp.order_group)
        orders = calc_total_sales(sku_sales_group_period)
        cost += comp.order_group.cost(orders)*orders
    return cost
    