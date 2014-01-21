from django.shortcuts import redirect
import django_tables2 as tables
import SkeletalDisplay.views_base as viewb
import SkeletalDisplay.views as sk_views
from django.core.urlresolvers import reverse
import SkeletalDisplay
import SalesEstimates.worker as worker
import traceback
import SalesEstimates.models as m
from django.db import models as db_models
import settings

class TabsMixin:
    def generate_tabs(self, active):
        tabs=[{'url': 'process', 'name': 'Setup', 'glyph': 'arrow-right'}]
        tabs.append({'url': 'generate', 'name': 'Generate Sales Estimates', 'glyph': 'flash'})
        tabs.append({'url': 'results', 'name': 'Results', 'glyph': 'fire'})
        for tab in tabs:
            if tab['url'] == active:
                tab['class'] = 'active'
            tab['url'] = reverse(tab['url'])
        self._context['tabs'] = tabs
        self.request.session['extra_context'] = {'tabs': tabs}

class Index(viewb.TemplateBase):
    template_name = 'index.html'
    side_menu = False
    all_auth_permitted = True
    
    def setup_context(self, **kw):
        self.request.session['top_active'] = None
        super(Index, self).setup_context(**kw)
    
    def get_context_data(self, **kw):
        self._context['title'] = settings.SITE_TITLE
        self._context['base_template'] = 'sk_page_base.html'
        return self._context

class SetupDisplayModel(sk_views.DisplayModel, TabsMixin):
    top_active = 'process'
    
    def setup_context(self, **kw):
        kw['app'] = 'salesestimates'
        if 'model' not in kw:
            kw['model'] = 'Manufacturer'
        super(SetupDisplayModel, self).setup_context(**kw)
        self.generate_tabs('process')
        
class SetupDisplayItem(sk_views.DisplayItem, TabsMixin):
    top_active = 'process'
    
    def setup_context(self, **kw):
        kw['app'] = 'salesestimates'
        super(SetupDisplayItem, self).setup_context(**kw)
        self.generate_tabs('process')

class Generate(viewb.TemplateBase, TabsMixin):
    template_name = 'generate.html'
    top_active = 'process'
    side_menu = False
    worker_funcs={'gcsp': {'func': worker.generate_customer_sp, 'msg': 'Successfully Generated Customer Sales Periods'},
                  'gskusales': {'func': worker.generate_skusales, 'msg': 'Successfully Generated Sales Estimates'}}
    
    def setup_context(self, **kw):
        super(Generate, self).setup_context(**kw)
        self.generate_tabs('generate')
    
    def get_context_data(self, **kw):
        self._context['title'] = 'Generate Sales Estimates'
        self._context['options'] = self.set_links()
        self.choose_func(kw)
        return self._context
    
    def set_links(self):
        links= []
        links.append({'url': reverse('generate', kwargs={'command': 'gcsp'}), 'name': 'Generate Customer Sales Periods (required after changes to Customers or Store Counts)'})
        links.append({'url': reverse('generate', kwargs={'command': 'gskusales'}), 'name': 'Generate Sales Estimates (required after any other changes)'})
        return links
        
    def choose_func(self, kw):
        if 'command' in kw:
            command = kw['command']
            if command in self.worker_funcs:
                self.do(**self.worker_funcs[command])
            else:
                name = self.__class__.__name__
                self._context['errors'] = ['%s does not have function for command %s' % (name, command)]
            
    def do(self, func=None, msg=None):
        logger = SkeletalDisplay.Logger()
        try:
            func(logger.addline)
        except Exception, e:
            error_msg = 'ERROR: %s' % str(e)
            self._context['errors'] = [error_msg]
            print error_msg
            traceback.print_exc()
        else:
            self._context['success'] = [msg]
        finally:
            self._context['info'] = logger.get_log()
            

class ResultsDisplayModel(sk_views.DisplayModel, TabsMixin):
    side_menu_items = ('SKUGroup', 'SKU', 'Customer')
    view_settings ={'viewname': 'results', 'args2include': [False, True], 'base_name': 'Results', 'top_active': 'process'}
    
    def setup_context(self, **kw):
        kw['app'] = 'salesestimates'
        if 'model' not in kw:
            kw['model'] = 'SKUGroup'
        super(ResultsDisplayModel, self).setup_context(**kw)
        self.generate_tabs('results')
        
class ResultsDisplayItem(sk_views.DisplayItem, TabsMixin):
    side_menu_items = ('SKUGroup', 'SKU', 'Customer')
    view_settings ={'viewname': 'results', 'args2include': [False, True], 'base_name': 'Results', 'top_active': 'process'}
    
    def setup_context(self, **kw):
        kw['app'] = 'salesestimates'
        super(ResultsDisplayItem, self).setup_context(**kw)
        self.generate_tabs('results')
        
    def get_context_data(self, **kw):
        self._context = super(ResultsDisplayItem, self).get_context_data(**kw)
        del self._context['page_menu']
        results_table = ResultsTable()
        self._context['tables_below'] = results_table.populate_table(self._item)
        return self._context

class DefaultMeta:
    orderable = False
    attrs = {'class': 'table table-bordered table-condensed'}
    per_page = 100

class ResultsTable:
    class DefaultTable(tables.Table):
        period = tables.Column()
        skus_sold = tables.Column(verbose_name='SKUs Sold')
        cost = SkeletalDisplay.SterlingPriceColumn(verbose_name='Cost')
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
        info = sku_sales.aggregate(skus_sold = db_models.Sum('sales'), cost = db_models.Sum('cost'), income = db_models.Sum('income'))
        row.update(info)
        return row

    def SKU(self, sp, sku):
        row={}
        sku_sales = m.SKUSales.objects.filter(period__period__id = sp.id, csku__sku__id=sku.id)
        info = sku_sales.aggregate(skus_sold = db_models.Sum('sales'), cost = db_models.Sum('cost'), income = db_models.Sum('income'))
        row.update(info)
        return row

    def SKUGroup(self, sp, group):
        row={}
        sku_sales = m.SKUSales.objects.filter(period__period__id = sp.id, csku__sku__group__id=group.id)
        info = sku_sales.aggregate(skus_sold = db_models.Sum('sales'), cost = db_models.Sum('cost'), income = db_models.Sum('income'))
        row.update(info)
        return row