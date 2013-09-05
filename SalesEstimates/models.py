from django.db import models
import settings
from django.core.exceptions import ObjectDoesNotExist

_default_imex_fields = ['xl_id', 'name', 'description', 'comment']

class BasicModel(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    xl_id = models.IntegerField('Excel ID', default=-1)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        abstract = True
    
class OrderGroup(BasicModel):
    nominal_price = models.DecimalField('Nominal price per unit', max_digits=6, decimal_places=4, null=True)
    minimum_order = models.IntegerField(default=0)
    lead_time = models.IntegerField('Lead Time (days)', default=0)
    
    imex_fields = _default_imex_fields + ['minimum_order', 'lead_time']
    imex_order = 0
    import_extra_func = 'import_costlevels'
    export_cls = 'OrderGroupExtra'
    
    def str_nominal_price(self):
        return price_str(self.nominal_price)
        
    class Meta:
        verbose_name_plural = 'Order Groups'
        verbose_name = 'Order Group'
    
class CostLevel(models.Model):
    order_group = models.ForeignKey(OrderGroup, related_name='costlevels')
    order_quantity = models.IntegerField(default=0)
    price = models.DecimalField('Price per unit', max_digits=6, decimal_places=2)
    
    def str_price(self):
        return price_str(self.price)
    
    def save(self, *args, **kwargs):
        super(CostLevel, self).save(*args, **kwargs)
        if self.order_group.costlevels.count() > 0:
            min_cost_level = self.order_group.costlevels.order_by('order_quantity')[0]
            if min_cost_level.order_quantity < self.order_quantity:
                return
        self.order_group.nominal_price = self.price
        self.order_group.save()
    
    def __unicode__(self):
        return '%s cost: %s @ %d units' % (self.order_group.name, price_str(self.price), self.order_quantity)

def price_str(value):
    if value is None:
        return '--'
    currency = u'\u00A3'
    if value >= 0.5:
        return '%s%0.2f' % (currency, value)
    else:
        return '%s%0.3f' % (currency, value)

class Component(BasicModel):
    order_group = models.ForeignKey(OrderGroup, related_name='components')
    
    imex_fields = _default_imex_fields + ['order_group']
    imex_order = 1
    export_cls = 'ComponentExtra'
    
    def str_nominal_price(self):
        return self.order_group.str_nominal_price()
        
    class Meta:
        verbose_name_plural = 'Components'
        verbose_name = 'Component'
    
class Assembly(BasicModel):
    size = models.CharField(max_length=200, null=True, blank=True)
    components = models.ManyToManyField(Component, related_name='assemblies')
    
    imex_fields = _default_imex_fields + ['size']
    imex_order = 2
    import_extra_func = 'import_Assembly_extra'
    export_cls = 'AssemblyExtra'
    
    def component_count(self):
        return self.components.count()
    
    def nominal_raw_cost(self):
        raw_cost = self.components.aggregate(models.Sum('order_group__nominal_price'))['order_group__nominal_price__sum']
        if raw_cost:
            return float(raw_cost)
        else:
            return None
    
    def str_nominal_raw_cost(self):
        return price_str(self.nominal_raw_cost())
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = 'Assemblies'
        verbose_name = 'Assembly'

class SKU(BasicModel):
    assemblies = models.ManyToManyField(Assembly, related_name='skus')
    dft_price = models.DecimalField('Default Sales Price', max_digits=6, decimal_places=2, null = True)
    
    imex_fields = _default_imex_fields + ['dft_price']
    imex_order = 3
    import_extra_func = 'import_SKU_extra'
    export_cls = 'SKUExtra'
    
    def assembly_count(self):
        return self.assemblies.count()
    
    def nominal_raw_cost(self):
        if self.assemblies.count() == 0:
            return '--'
        cost = 0
        for assy in self.assemblies.all():
            cost += assy.nominal_raw_cost()
        return cost
    
    def str_nominal_raw_cost(self):
        return price_str(self.nominal_raw_cost())
    
    def str_dft_price(self):
        return price_str(self.dft_price)
        
    class Meta:
        verbose_name_plural = 'SKUs'
        verbose_name = 'SKU'

class Customer(BasicModel):
    skus = models.ManyToManyField(SKU, related_name='customers', through='CustomerSKU')
    
    imex_fields = _default_imex_fields
    imex_order = 4
    
    def sku_count(self):
        return self.skus.count()
        
    class Meta:
        verbose_name_plural = 'Customers'
        verbose_name = 'Customer'

class CustomerSKU(models.Model):
    sku = models.ForeignKey(SKU, related_name='c_skus')
    customer = models.ForeignKey(Customer, related_name='c_skus')
    price = models.DecimalField('Sales Price', max_digits=6, decimal_places=2)
    xl_id = models.IntegerField('Excel ID', default=-1)
    
    imex_fields = ['xl_id', 'sku', 'customer', 'price']
    imex_order = 5
    export_cls = 'CustomerSKUExtra'
    
    def sku_name(self):
        return self.sku.name
    
    def customer_name(self):
        return self.customer.name
    
    def str_price(self):
        return price_str(self.price)
        
    def __unicode__(self):
        return '%s for %s' % (self.sku.name, self.customer.name)
        
    class Meta:
        verbose_name_plural = 'Customer SKUs'
        verbose_name = 'Customer SKU'

class SalesPeriod(models.Model):
    start_date = models.DateField()
    finish_date = models.DateField()
    customers = models.ManyToManyField(Customer, related_name='sales_periods', through='CustomerSalesPeriod')
    
    def str_start(self):
        return self.start_date.strftime(settings.CUSTOM_DATE_FORMAT)
    
    def str_finish(self):
        return self.finish_date.strftime(settings.CUSTOM_DATE_FORMAT)
    
    def length_days(self):
        return (self.finish_date - self.start_date).days
    
    def __unicode__(self):
        return '%s to %s, %d days' % (self.str_start(), self.str_finish(), self.length_days())

    class Meta:
        verbose_name_plural = 'Sales Periods'
        verbose_name = 'Sales Period'
        
class CustomerSalesPeriod(models.Model):
    customer = models.ForeignKey(Customer, related_name='c_sales_periods')
    period = models.ForeignKey(SalesPeriod, related_name='c_sales_periods')
    store_count = models.IntegerField(default=0)
    
    def str_period(self):
        return '%s to %s' % (self.period.start_date.strftime(settings.CUSTOM_DATE_FORMAT),
                             self.period.finish_date.strftime(settings.CUSTOM_DATE_FORMAT))
    
    def __unicode__(self):
        return 'period from %s for %s, %d stores' % (self.period.start_date.strftime(settings.CUSTOM_DATE_FORMAT),
                                                      self.customer.name, self.store_count)

class SKUSales(models.Model):
    period = models.ForeignKey(CustomerSalesPeriod, related_name='sku_sales')
    csku = models.ForeignKey(CustomerSKU, related_name='sku_sale')
    sales = models.IntegerField(default=0)
    
    def sku_name(self):
        return self.csku.sku_name()
    
    def __unicode__(self):
        return '%s sells %d at %s starting %s' % (self.sku_name(), self.sales, self.period.customer.name,  
                                            self.period.period.start_date.strftime(settings.CUSTOM_DATE_FORMAT))
    
    class Meta:
        verbose_name_plural = 'SKU Sales'
        verbose_name = 'SKU Sales'