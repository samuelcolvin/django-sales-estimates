from django.db import models
import settings

currency = u'\u00A3'

class BasicModel(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        abstract = True
        
class Component(BasicModel):
    minimum_order = models.IntegerField(default=0)
    nominal_price = models.DecimalField('Nominal cost per unit', max_digits=6, decimal_places=2, null=True)
    
    def str_nominal_price(self):
        return '%s%0.2f' % (currency, self.nominal_price)
    
class CostLevel(models.Model):
    component = models.ForeignKey(Component, related_name='costlevels')
    order_quantity = models.IntegerField(default=0)
    price = models.DecimalField('Price per unit', max_digits=6, decimal_places=2)
    
    def str_price(self):
        return '%s%0.2f' % (currency, self.price)
    
    def save(self, *args, **kwargs):
        super(CostLevel, self).save(*args, **kwargs)
        if self.component.costlevels.count() > 0:
            min_cost_level = self.component.costlevels.order_by('order_quantity')[0]
            if min_cost_level.order_quantity < self.order_quantity:
                return
        self.component.nominal_price = self.price
        self.component.save()
    
    def __unicode__(self):
        return '%s cost: %0.2f @ %d units' % (self.component.name, self.price, self.order_quantity)
    
class Assembly(models.Model):
    name = models.CharField(max_length=200)
    components = models.ManyToManyField(Component, related_name='assemblies')
    
    def component_count(self):
        return self.components.count()
    
    def nominal_raw_cost(self):
        return float(self.components.aggregate(models.Sum('nominal_price'))['nominal_price__sum'])
    
    def str_nominal_raw_cost(self):
        return '%s%0.2f' % (currency, self.nominal_raw_cost())
    
    def __unicode__(self):
        return self.name

class SKU(BasicModel):
    assemblies = models.ManyToManyField(Assembly, related_name='skus')
    dft_price = models.DecimalField('Default Sales Price', max_digits=6, decimal_places=2)
    
    def assembly_count(self):
        return self.assemblies.count()
    
    def nominal_raw_cost(self):
        cost = 0
        for assy in self.assemblies.all():
            cost += assy.nominal_raw_cost()
        return cost
        
    class Meta:
        verbose_name_plural = 'SKUs'
        verbose_name = 'SKU'

class Customer(BasicModel):
    skus = models.ManyToManyField(SKU, related_name='customers', through='CustomerSKU')
    
    def sku_count(self):
        return self.skus.count()

class CustomerSKU(models.Model):
    sku = models.ForeignKey(SKU, related_name='c_skus')
    customer = models.ForeignKey(Customer, related_name='c_skus')
    price = models.DecimalField('Sales Price', max_digits=6, decimal_places=2)
    
    def sku_name(self):
        return self.sku.name
    
    def str_price(self):
        return '%s%0.2f' % (currency, self.price)
        
    def __unicode__(self):
        return '%s for %s' % (self.sku.name, self.customer.name)
        
    class Meta:
        verbose_name_plural = 'Customer SKUs'
        verbose_name = 'Customer SKU'
    
class SalesPeriod(models.Model):
    start_date = models.DateField()
    finish_date = models.DateField()
    customers = models.ManyToManyField(Customer, related_name='sales_periods', through='CustomerSalesPeriod')
    
    def __unicode__(self):
        return '%s to %s' % (self.start_date.strftime(settings.CUSTOM_DATE_FORMAT),
                             self.finish_date.strftime(settings.CUSTOM_DATE_FORMAT))

class CustomerSalesPeriod(models.Model):
    customer = models.ForeignKey(Customer, related_name='c_sales_periods')
    period = models.ForeignKey(SalesPeriod, related_name='c_sales_periods')
    store_count = models.IntegerField(default=0)
    
    def __unicode__(self):
        return '%s for %s, %d stores' % (str(self.period), self.customer.name, self.store_count)

class SKUSales(models.Model):
    period = models.ForeignKey(CustomerSalesPeriod, related_name='sku_sales_estimates')
    sku = models.ForeignKey(SKU, related_name='sku_sales_estimates')
    sales = models.IntegerField(default=0)
    
    def __unicode__(self):
        return '%s sells %d at %s during %s' % (self.sku.name, self.sales, self.period.customer.name,  
                                            str(self.period))
        
    class Meta:
        verbose_name_plural = 'SKU Sales'
        verbose_name = 'SKU Sales'
    