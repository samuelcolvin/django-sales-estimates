from django.shortcuts import redirect
import SkeletalDisplay.views_base as viewb
import SkeletalDisplay.views as sk_views
from django.core.urlresolvers import reverse
import SkeletalDisplay
import SalesEstimates.worker as worker
import SalesEstimates.models as m

class TabsMixin:
    def generate_tabs(self, active):
        tabs=[{'url': 'process', 'name': 'Setup', 'glyph': 'arrow-right'}]
        tabs.append({'url': 'generate_cskui', 'name': 'Generate Customer SKU Info', 'glyph': 'fire'})
        tabs.append({'url': 'process_alter', 'name': 'Alter Customer SKU Info', 'glyph': 'arrow-right'})
        tabs.append({'url': 'process', 'name': 'Generate Sales Estimates', 'glyph': 'fire'})
        for tab in tabs:
            if tab['url'] == active:
                tab['class'] = 'active'
            tab['url'] = reverse(tab['url'])
        self._context['tabs'] = tabs

class SetupIndex(viewb.TemplateBase, TabsMixin):
    template_name = 'progress_setup.html'
    top_active = 'process'
    viewname = 'process'
    base_name = 'Process'
    include_appname_in_args = False
    side_menu_items = ('Manufacturer', 'OrderGroup', 'Component', 'Assembly', 
                       'SKUGroup', 'SeasonalVariation', 'SKU', 'Customer')
    
    def get_context_data(self, **kw):
        self._context['title'] = 'Setup'
        self.generate_tabs('process')
        return self._context

class SetupDisplayModel(sk_views.DisplayModel, TabsMixin):
    top_active = 'process'
    viewname = 'process'
    base_name = 'Process'
    include_appname_in_args = False
    side_menu_items = ('Manufacturer', 'OrderGroup', 'Component', 'Assembly', 
                       'SKUGroup', 'SeasonalVariation', 'SKU', 'Customer')
    
    def setup_context(self, **kw):
        kw['app'] = 'salesestimates'
        super(SetupDisplayModel, self).setup_context(**kw)
        self.generate_tabs('process')
        
class SetupDisplayItem(sk_views.DisplayItem, TabsMixin):
    top_active = 'process'
    viewname = 'process'
    include_appname_in_args = False
    side_menu_items = ('Manufacturer', 'OrderGroup', 'Component', 'Assembly', 
                       'SKUGroup', 'SeasonalVariation', 'SKU', 'Customer')
    
    def setup_context(self, **kw):
        kw['app'] = 'salesestimates'
        super(SetupDisplayItem, self).setup_context(**kw)
        self.generate_tabs('process')

class GenerateCUSKI(viewb.TemplateBase, TabsMixin):
    template_name = 'generate.html'
    top_active = 'process'
    base_name = 'Process'
    side_menu = False
    
    def setup_context(self, **kw):
        super(GenerateCUSKI, self).setup_context(**kw)
        self.generate_tabs('generate_cskui')
    
    def get_context_data(self, **kw):
        self._context['title'] = 'Generate Customer SKU Info'
        self._context['page_menu'] = self.set_links()
        if 'command' in kw:
            if kw['command'] == 'gcski':
                self.generate_cski()
            if kw['command'] == 'gcsp':
                self.generate_csp()
        return self._context
    
    def generate_cski(self):
        logger = SkeletalDisplay.Logger()
        try:
            worker.generate_cskui(logger.addline)
        except Exception, e:
            self._context['errors'] = ['ERROR: %s' % str(e)]
        else:
            self._context['success'] = ['Successfully Generate Customer SKU Info']
        finally:
            self._context['info'] = logger.get_log()
            
    def generate_csp(self):
        logger = SkeletalDisplay.Logger()
        try:
            worker.generate_customer_sp(logger.addline)
        except Exception, e:
            self._context['errors'] = ['ERROR: %s' % str(e)]
        else:
            self._context['success'] = ['Successfully Generate Customer Sales Periods']
        finally:
            self._context['info'] = logger.get_log()
    
    def set_links(self):
        links = [{'url': reverse('generate_cskui', kwargs={'command': 'gcski'}), 'name': 'Generate Customer SKU Information'}]
        links.append({'url': reverse('delete_all_cskui'), 'name': 'Delete All Customer SKU Information'})
        links.append({'url': reverse('generate_cskui', kwargs={'command': 'gcsp'}), 'name': 'Generate Customer Sales Periods'})
        return links

def delete_all_cskui(request):
    items = m.CustomerSKUInfo.objects.all()
    msg= 'Deleted %d CustomerSKUInfo groups' % items.count()
    items.delete()
    request.session['success']=[msg]
    return redirect(reverse('generate_cskui'))
    
class AlterDisplayModel(sk_views.DisplayModel, TabsMixin):
    top_active = 'process'
    viewname = 'process_alter'
    base_name = 'Alter'
    include_appname_in_args = False
    side_menu_items = ('CustomerSKUInfo', 'SalesPeriod')
    
    def setup_context(self, **kw):
        kw['app'] = 'salesestimates'
        if 'model' not in kw:
            kw['model'] = 'CustomerSKUInfo'
        super(AlterDisplayModel, self).setup_context(**kw)
        self.generate_tabs('process_alter')
        
class AlterDisplayItem(sk_views.DisplayItem, TabsMixin):
    top_active = 'process'
    viewname = 'process_alter'
    base_name = 'Alter'
    include_appname_in_args = False
    side_menu_items = ('CustomerSKUInfo', 'SalesPeriod')
    
    def setup_context(self, **kw):
        kw['app'] = 'salesestimates'
        super(AlterDisplayItem, self).setup_context(**kw)
        self.generate_tabs('process_alter')