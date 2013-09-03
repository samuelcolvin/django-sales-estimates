import settings
from datetime import datetime as dtdt
from datetime import timedelta as td

import SalesEstimates.models as m

def generate_sales_periods(log_output):
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
        
    log_output('\nadding periods to db...')
    for period in periods:
        existing = m.SalesPeriod.objects.filter(start_date = period['start'], finish_date = period['finish'])
        if existing.count() > 0:
            log_output('  ALREADY EXISTS: %s' % existing[0])
        else:
            p = m.SalesPeriod.objects.create(start_date = period['start'], finish_date = period['finish'])
            log_output('ADDED: %s' % p)
        
def populate_sales_periods(log_output):
    for period in m.SalesPeriod.objects.all():
        for customer in m.Customer.objects.all():
            existing = m.CustomerSalesPeriod.objects.filter(customer=customer, period=period)
            if existing.count() > 0:
                log_output('CSP ALREADY EXISTS: %s' % existing[0])
            else:
                csp = m.CustomerSalesPeriod.objects.create(customer=customer, period=period)
                log_output(' CSP ADDED: %s' % csp)
            for csku in customer.c_skus.all():
                existing = m.SKUSales.objects.filter(period=period, csku=csku)
                if existing.count() == 0:
                    s_sales = m.SKUSales.objects.create(period=period, csku=csku)
                    log_output('  SKU Sales added: %s' % s_sales)
                
                    
                
                    