from django.shortcuts import redirect
import django_tables2 as tables
import SkeletalDisplay.views_base as viewb
import SkeletalDisplay.views as sk_views
from django.core.urlresolvers import reverse
import SkeletalDisplay
import SalesEstimates.worker.actions as worker
import traceback
import SalesEstimates.models as m
from django.db import models as db_models
import settings

class Index(viewb.TemplateBase):
    template_name = 'sk_nvd3.html'
    side_menu = False
    all_auth_permitted = True
    
    def setup_context(self, **kw):
        self.request.session['top_active'] = None
        super(Index, self).setup_context(**kw)
    
    def get_context_data(self, **kw):
        self._context['title'] = settings.SITE_TITLE
        return self._context

class SetupDisplayModel(sk_views.DisplayModel):
    top_active = 'setup'
    
    def setup_context(self, **kw):
        kw['app'] = 'salesestimates'
        if 'model' not in kw:
            kw['model'] = 'Manufacturer'
        super(SetupDisplayModel, self).setup_context(**kw)
        
class SetupDisplayItem(sk_views.DisplayItem):
    top_active = 'setup'
    
    def setup_context(self, **kw):
        kw['app'] = 'salesestimates'
        super(SetupDisplayItem, self).setup_context(**kw)

class Generate(viewb.TemplateBase):
    template_name = 'generate.html'
    top_active = None
    side_menu = False
    
    def setup_context(self, **kw):
        super(Generate, self).setup_context(**kw)
    
    def get_context_data(self, **kw):
        self._context['title'] = 'Generate Sales Estimates' 
        self._context['pre_top_menu'] = self._context['pre_top_menu'].\
            replace('class="pre-top', 'class="pre-top active')
        self._context['options'] = self.set_links()
        logger = SkeletalDisplay.Logger()
        try:
            worker.generate_skusales(logger.addline)
        except Exception, e:
            error_msg = 'ERROR: %s' % str(e)
            self._context['errors'] = [error_msg]
            print error_msg
            traceback.print_exc()
        else:
            self._context['success'] = ['Successfully Generated Sales Estimates']
            self._context['pre_top_menu'] = self._context['pre_top_menu'].replace('pre-top-active', '')
        finally:
            self._context['info'] = logger.get_log()
        return self._context

side_bar = ('Order', 'SKUGroup', 'SKU', 'Customer')
class ResultsDisplayModel(sk_views.DisplayModel):
    side_menu_items = side_bar
    view_settings ={'viewname': 'results', 'args2include': [False, True], 'base_name': 'Results', 'top_active': 'results'}
    
    def setup_context(self, **kw):
        kw['app'] = 'salesestimates'
        if 'model' not in kw:
            kw['model'] = 'SKUGroup'
        super(ResultsDisplayModel, self).setup_context(**kw)
        
class ResultsDisplayItem(sk_views.DisplayItem):
    side_menu_items = side_bar
    view_settings ={'viewname': 'results', 'args2include': [False, True], 'base_name': 'Results', 'top_active': 'results'}
    custom_tables_below = True
    
    def setup_context(self, **kw):
        kw['app'] = 'salesestimates'
        super(ResultsDisplayItem, self).setup_context(**kw)
        
    def get_context_data(self, **kw):
        self._context = super(ResultsDisplayItem, self).get_context_data(**kw)
        del self._context['page_menu']
        if self._model_name != 'Order':
            results_table = ResultsTable()
            self._context['tables_below'] = results_table.populate_table(self._item)
        return self._context

class DefaultMeta:
    orderable = False
    attrs = {'class': 'table table-bordered table-condensed'}
    per_page = 500

class ResultsTable:
    class DefaultTable(tables.Table):
        period = tables.Column()
        skus_sold = tables.Column(verbose_name='SKUs Sold')
        income = SkeletalDisplay.SterlingPriceColumn(verbose_name='Income')
        Meta = DefaultMeta
            
    class CustomerTable(DefaultTable):
        store_count = tables.Column(verbose_name='Store Count')
        Meta = DefaultMeta
        
    def populate_table(self, item):
        this_table={'title': 'Sales Periods'}
        content = []
        func = getattr(self, item.__class__.__name__)
        for sp in m.SalesPeriod.objects.all():
            row = func(sp, item)
            row['period'] = sp.str_simple_date()
            content.append(row)
        t_name = item.__class__.__name__ + 'Table'
        if hasattr(self, t_name):
            table = getattr(self, t_name)
        else:
            table = self.DefaultTable
        this_table['renderable'] = table(content)
        return [this_table]
        
    def Customer(self, sp, customer):
        row={}
        csp = m.CustomerSalesPeriod.objects.filter(customer = customer).filter(period = sp)[0]
        row['store_count'] = csp.store_count
        sku_sales = m.SKUSales.objects.filter(period__period__id = sp.id, csku__customer__id=customer.id)
        info = sku_sales.aggregate(skus_sold = db_models.Sum('sales'), income = db_models.Sum('income'))
        row.update(info)
        return row

    def SKU(self, sp, sku):
        row={}
        sku_sales = m.SKUSales.objects.filter(period__period__id = sp.id, csku__sku__id=sku.id)
        info = sku_sales.aggregate(skus_sold = db_models.Sum('sales'), income = db_models.Sum('income'))
        row.update(info)
        return row

    def SKUGroup(self, sp, group):
        row={}
        sku_sales = m.SKUSales.objects.filter(period__period__id = sp.id, csku__sku__group__id=group.id)
        info = sku_sales.aggregate(skus_sold = db_models.Sum('sales'), income = db_models.Sum('income'))
        row.update(info)
        return row