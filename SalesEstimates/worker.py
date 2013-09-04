import settings
from datetime import datetime as dtdt
from datetime import timedelta as td

import SalesEstimates.models as m
from django.utils.encoding import smart_text
import openpyxl, re
from django.db import models
import inspect
from django.core.exceptions import ObjectDoesNotExist

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
            m.SalesPeriod.objects.create(start_date = period['start'], finish_date = period['finish'])
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

class ReadXl:
    def __init__(self, fname, log):
        self._log = log
        self._log('loading "%s"' % fname)
        self._wb = openpyxl.load_workbook(fname)
        self._log('Worksheets: %s' % str(self._wb.get_sheet_names()))
        self._unichar_finder = re.compile(r'[^\x00-\xff]')
        self._dft_fields = ['xl_id', 'name', 'description', 'comment']
        self._sheet = 'unknown'
        self._row = 0
        try:
            self._import_OrderGroup()
            self._import_Component()
            self._import_Assembly()
            self._import_SKU()
            self._import_Customers()
            self._import_CustomerSKUs()
        except Exception, e:
            self._log('Error on sheet %s, row %d' % (self._sheet, self._row))
            self._log(str(e))
            
    def _import_OrderGroup(self):
        fields = self._dft_fields[:]
        fields.extend(['minimum_order', 'lead_time'])
        self._import_sheet(m.OrderGroup, fields, self._import_costlevels)
        self._log('imported %d Order Groups with %d associated Cost Levels' %
                  (m.OrderGroup.objects.count(), m.CostLevel.objects.count()))
        
    def _import_Component(self):
        fields = self._dft_fields[:]
        fields.extend(['order_group'])
        self._import_sheet(m.Component, fields)
        self._log('imported %d Components' % m.Component.objects.count())
        
    def _import_Assembly(self):
        fields = self._dft_fields[:]
        fields.extend(['size'])
        self._m2m_field_name = 'components'
        self._m2m_model = m.Component
        self._import_sheet(m.Assembly, fields, self._import_m2m)
        self._log('imported %d Assemblies' % m.Assembly.objects.count())
        
    def _import_SKU(self):
        fields = self._dft_fields[:]
        fields.extend(['dft_price'])
        self._m2m_field_name = 'assemblies'
        self._m2m_model = m.Assembly
        self._import_sheet(m.SKU, fields, self._import_m2m)
        self._log('imported %d SKUs' % m.SKU.objects.count())
        
    def _import_Customers(self):
        self._import_sheet(m.Customer, self._dft_fields)
        self._log('imported %d Customers' % m.Customer.objects.count())
        
    def _import_CustomerSKUs(self):
        fields = ['xl_id', 'sku', 'customer', 'price']
        self._import_sheet(m.CustomerSKU, fields)
        self._log('imported %d Customer SKUs' % m.CustomerSKU.objects.count())
        
    def _import_costlevels(self, ws, order_group, row):
        if not hasattr(self, '_CL_heads'):
            cl_heads = filter(lambda x: x.startswith('costlevels'), self._headings.keys())
            self._CL_heads = {}
            for cl_head in cl_heads:
                self._CL_heads[cl_head] = int(cl_head.replace('costlevels', ''))
        for cl_head in self._CL_heads:
            value = ws.cell(row=row, column=self._headings[cl_head]).value
            if value is not None:
                m.CostLevel.objects.create(order_group=order_group, 
                                           order_quantity = self._CL_heads[cl_head],
                                           price=value)
        
    def _import_m2m(self, ws, main_item, row):
        main_i_field = getattr(main_item, self._m2m_field_name)
        for comp_col in self._headings[self._m2m_field_name]:
            value = ws.cell(row=row, column=comp_col).value
            if value is not None:
                try:
                    main_i_field.add(self._m2m_model.objects.get(xl_id=value))
                except ObjectDoesNotExist:
                    raise Exception('ERROR: item with xl_id = %d does not exist in %s' % (value, self._m2m_model.__name__))
    
    def _import_sheet(self, model, fields, extra_func = None, p = False):
        self._sheet = model.__name__
        ws = self._wb.get_sheet_by_name(name = self._sheet)
        self._headings = self._get_headings(ws)
        if p:
            self._log('column names: %s' % str(self._headings))
        for self._row in range(1, ws.get_highest_row()):
            main_item = model()
            for field in fields:
                value = ws.cell(row=self._row, column=self._headings[field]).value
                if p:
                    self._log('%s: %s' % (field, self._clean_string(value)))
                field_info = model._meta.get_field_by_name(field)[0]
                if isinstance(field_info, models.fields.related.ForeignKey):
                    if value is not None:
                        try:
                            value = field_info.rel.to.objects.get(xl_id = value)
                        except ObjectDoesNotExist:
                            raise Exception('ERROR: item with xl_id = %d does not exist in %s' % (value, field_info.rel.to.__name__))
                else:
                    value = self._get_value(getattr(main_item, field), value)
                setattr(main_item, field, value)
            main_item.save()
            if extra_func:
                extra_func(ws, main_item, self._row)

    def _get_headings(self, ws):
        headings={}
        col_number = 0
        while True:
            name = ws.cell(row=0, column = col_number).value
            if name is None:
                break
            elif name in headings:
                if isinstance(headings[name], list):
                    headings[name].append(col_number)
                else:
                    headings[name] = [headings[name], col_number]
            else:
                headings[name] = col_number
            col_number += 1
        return headings
    
    def _get_value(self, field, value):
        if value is None:
            return None
        elif isinstance(field, int) or isinstance(field, float):
            return value
        elif isinstance(field, str):
            return self._clean_string(value)
        else:
            return value
    
    def _clean_string(self, s):
            s = smart_text(s)
            return re.sub(self._unichar_finder, '', s)
            
def clear_se(log):
    for mod_name in dir(m):
        mod = getattr(m, mod_name)
        if inspect.isclass(mod)  and issubclass(mod, models.Model) and not mod._meta.abstract:
            mod.objects.all().delete()
            log('Deleting all records from %s' % mod.__name__)






