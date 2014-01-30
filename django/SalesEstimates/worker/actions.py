import settings
from datetime import datetime as dtdt
from datetime import timedelta as td

import SalesEstimates.models as m
from django.db import models as db_models
import inspect
import decimal
from django.db import transaction
from time import time
import _utils
from django.db import connection

def generate_sales_periods(log):
    start_date = dtdt.strptime(settings.SALES_PERIOD_START_DATE, settings.CUSTOM_DATE_FORMAT)
    system_finish_date = dtdt.strptime(settings.SALES_PERIOD_FINISH_DATE, settings.CUSTOM_DATE_FORMAT)
    week_start_day = 0
    if hasattr(settings, 'WEEK_START_DAY'):
        week_start_day = settings.WEEK_START_DAY
    aday = td(days=1)
    while start_date.weekday() != week_start_day:
        start_date += aday
    
    periods = []
    while True:
        next_start_date = start_date + aday * 7
        finish_date = next_start_date - aday
        if finish_date > system_finish_date:
            break
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
    
# def generate_customer_sp(log):
#     start = time()
#     mysql, msgs = _utils.get_con()
#     msgs += mysql.clear_csp()
#     msgs += mysql.generate_csp()
#     print msgs
#     [log(msg) for msg in msgs.split('\n')]
#     log('Time taken: %0.3f seconds' % (time() - start))

def generate_skusales(log):
    msgs = _utils.generate_skusales()
    company = m.Company.objects.get(id=settings.DEFAULT_COMPANY)
    company.results_status = 0
    company.save()
    print msgs
    [log(msg) for msg in msgs.split('\n')]

def delete_before_upload(log):
    clear_se(log)
    generate_sales_periods(log)
        
def clear_se(log):
    cursor = connection.cursor()
    for mod_name in dir(m):
        if mod_name == 'User':
            continue
        mod = getattr(m, mod_name)
        if inspect.isclass(mod)  and issubclass(mod, db_models.Model) and not mod._meta.abstract:
            mod.objects.all().delete()
            log('Deleting all records from %s' % mod.__name__)
            cursor.execute('ALTER TABLE %s AUTO_INCREMENT = 1' % mod._meta.db_table)