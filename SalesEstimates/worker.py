import settings
from datetime import datetime as dtdt
from datetime import timedelta as td

import SalesEstimates.models as m
from django.db import models as db_models
import inspect, operator

import SkeletalDisplay
from SkeletalDisplay.views import base as skeletal_base
import decimal

def generate(request):
    apps = SkeletalDisplay.get_display_apps()
    logger = SkeletalDisplay.Logger()
    generate_auto_sales_figures(logger.addline)
    content = {'log': logger.get_log()}
    return skeletal_base(request, 'Generate Sales Estimates', content, 'generate.html', apps)

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
        
# def populate_sales_periods(log):
#     log('Creating customer sales periods and SKU sales periods...')
#     for period in m.SalesPeriod.objects.all():
#         for customer in m.Customer.objects.all():
#             csp = m.CustomerSalesPeriod.objects.filter(customer=customer, period=period)
#             if csp.count() > 0:
#                 csp = csp[0]
#             else:
#                 csp = m.CustomerSalesPeriod.objects.create(customer=customer, period=period)
#             for csku in customer.c_skus.all():
#                 existing = m.SKUSales.objects.filter(period=csp, csku=csku)
#                 if existing.count() == 0:
#                     m.SKUSales.objects.create(period=csp, csku=csku)
#     log('Created %d customer sales periods and %s sku sales periods' % 
#         (m.CustomerSalesPeriod.objects.count(), m.SKUSales.objects.count()))

def generate_auto_sales_figures(log):
    sku_count = 0
    decimal.getcontext().prec = 4
    for csp in m.CustomerSalesPeriod.objects.all():
        for csku in m.CustomerSKU.objects.all():
            existing =m.SKUSales.objects.filter(period=csp, csku=csku)
            if existing.count() > 1:
                log('repeated SKUSales for csp = %s and csku = %' % (csp, csku))
                existing.delete()
                sku_sales = m.SKUSales(period=csp, csku=csku)
            elif existing.count() == 1:
                sku_sales = existing[0]
                existing = True
            else:
                sku_sales = m.SKUSales(period=csp, csku=csku)
                existing = False
                sku_count += 1
            if csp.store_count != None and csku.sale_rate != None:
                sku_sales.sales = csp.store_count * csku.sale_rate * settings.SALES_PERIOD_LENGTH * 4
                sku_sales.income = decimal.Decimal(sku_sales.sales) * sku_sales.csku.price
                sku_sales.save()
            elif existing:
                sku_sales.delete()
    for sku_sales in m.SKUSales.objects.all():
        sku_sales.cost = calc_sku_sales_cost(sku_sales)
        sku_sales.save()
#     for period in m.SalesPeriod.objects.all():
#         order_group_info = {}
#         for order_group in m.OrderGroup.objects.all():
#             sku_sales_group_period = m.SKUSales.objects.filter(period=period).filter(csku__sku__assemblies__components__order_group=order_group)
#             orders = calc_total_sales(sku_sales_group_period)
#             if orders is not None:
#                 cost = order_group.cost(orders)*orders
#             else:
#                 cost = 0
#             order_group_info[order_group.pk] = (orders, cost)
#         for sku_sales in m.SKUSales.objects.filter(period__period = period):
#             order_groups = m.Component.objects.filter(order_group__components__assemblies__skus__c_skus__sku_sales = sku_sales).values_list('order_group__pk',flat=True)
#             sku_sales.cost = sum([order_group_info[og][1] for og in order_groups])
#             sku_sales.save()

    log('%d SKU sale quantities calculated' % sku_count)
        

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
    for comp in m.Component.objects.filter(assemblies__skus__c_skus__sku_sales=sku_sales):
        sku_sales_group_period = m.SKUSales.objects.filter(period__period=sp).filter(csku__sku__assemblies__components__order_group=comp.order_group)
        orders = calc_total_sales(sku_sales_group_period)
        cost += comp.order_group.cost(orders)*orders
    return cost
    