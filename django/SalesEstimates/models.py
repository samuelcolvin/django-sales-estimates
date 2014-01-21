from django.db import models
import settings

class BasicModel(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    xl_id = models.IntegerField('Excel ID', default=-1, editable=False)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        abstract = True
        
class Manufacturer(BasicModel):
    pass
    class Meta:
        verbose_name_plural = 'Manufacturers'
        verbose_name = 'Manufacturer'

class OrderGroup(BasicModel):
    nominal_price = models.DecimalField('Nominal price per unit', max_digits=11, decimal_places=4, null=True, blank=True)
    minimum_order = models.IntegerField(default=0)
    lead_time = models.IntegerField('Lead Time (days)', default=0)
    manufacturer = models.ForeignKey(Manufacturer, related_name='order_group')
    
    def cost(self, orders):
        costlevels_avail = self.costlevels.filter(order_quantity__lte = orders)
        if costlevels_avail.exists():
            return costlevels_avail.order_by('-order_quantity')[0].price
        else:
            if self.costlevels.exists():
                return self.costlevels.order_by('order_quantity')[0].price
            else:
                return 0
    
    def str_nominal_price(self):
        return price_str(self.nominal_price)
        
    class Meta:
        verbose_name_plural = 'Order Groups'
        verbose_name = 'Order Group'
    
class CostLevel(models.Model):
    order_group = models.ForeignKey(OrderGroup, related_name='costlevels')
    order_quantity = models.IntegerField(default=0)
    price = models.DecimalField('Price per unit', max_digits=11, decimal_places=2)
    
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
    
    class Meta:
        ordering = ['order_quantity']

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
    
    def get_manufacturer(self):
        return self.order_group.manufacturer
    
    def str_nominal_price(self):
        return self.order_group.str_nominal_price()
        
    class Meta:
        verbose_name_plural = 'Components'
        verbose_name = 'Component'
    
class Assembly(BasicModel):
    size = models.CharField(max_length=200, null=True, blank=True)
    components = models.ManyToManyField(Component, through='AssyComponent', related_name='assemblies')
    
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

class AssyComponent(models.Model):
    xl_id = models.IntegerField('Excel ID', default=-1, editable=False)
    component = models.ForeignKey(Component)
    assembly = models.ForeignKey(Assembly)
    count = models.IntegerField(default = 1)

class SKUGroup(BasicModel):
    pass

    class Meta:
        verbose_name_plural = 'SKU Groups'
        verbose_name = 'SKU Group'

class SeasonalVariation(BasicModel):
    pass
    
    def month_count(self):
        return self.months.count()
    
    class Meta:
        verbose_name_plural = 'Seasonal Variations'
        verbose_name = 'Seasonal Variation'

class MonthVariation(models.Model):
    MONTHS=(
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    )
    month = models.IntegerField('Month', choices=MONTHS)
    srf = models.FloatField('Sale Rate Factor', default=1)
    season_var = models.ForeignKey(SeasonalVariation, related_name='months')
    
    def __unicode__(self):
        return '%s, rate: %0.2f' % (self.get_month_display(), self.srf)
    
    class Meta:
        unique_together = (('season_var', 'month'),)

class SKU(BasicModel):
    assemblies = models.ManyToManyField(Assembly, related_name='skus')
    dft_price = models.DecimalField('Default Sales Price', max_digits=11, decimal_places=2, null = True)
    dft_srf = models.FloatField('Default Sale Rate Factor', default = 1)
    dft_season_var = models.ForeignKey(SeasonalVariation, related_name='customers', verbose_name = 'Default Seasonal Variation')
    group = models.ForeignKey(SKUGroup, related_name='sku')
    
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
    dft_srf = models.FloatField('Default Sale Rate Factor', default = 1)
    dft_store_count = models.IntegerField(null = True, blank = True)
    
    def all_skus(self):
        return CustomerSKUInfo.objects.filter(customer=self)
    
    def sku_count(self):
        return self.all_skus().count()
        
    class Meta:
        verbose_name_plural = 'Customers'
        verbose_name = 'Customer'

class CustomerSKUInfo(models.Model):
    sku = models.ForeignKey(SKU, related_name='c_skus')
    customer = models.ForeignKey(Customer, related_name='c_skus')
    price = models.DecimalField('Sales Price', max_digits=11, decimal_places=2, null=True, blank=True)
    price.help_text = 'Leave blank to use the SKU default price'
    srf = models.FloatField('Sale Rate Factor', null = True, blank=True)
    srf.help_text = 'Leave blank to use the product of the Customer and SKU default (srf=customer srf default * sku srf default)'
    custom_srf = models.BooleanField('Has Custom Sale Rate Factor', default= True, editable=False)
    season_var = models.ForeignKey(SeasonalVariation, related_name='customer_skus', null = True, blank=True)
    season_var.help_text = 'Leave blank to use the SKU default seasonal variation'
    xl_id = models.IntegerField('Excel ID', default=-1, editable=False)
    
    def sku_name(self):
        return self.sku.name
    
    def customer_name(self):
        return self.customer.name
    
    def str_price(self):
        return price_str(self.price)
        
    def __unicode__(self):
        return '%s for %s' % (self.sku.name, self.customer.name)
        
    class Meta:
        unique_together = (('sku', 'customer'),)
        verbose_name_plural = 'Customer SKU Information'
        verbose_name = 'Customer SKU Information'
    
    def save(self, *args, **kwargs):
        super(CustomerSKUInfo, self).save(*args, **kwargs)
        editted = False
        if self.price is None and self.sku.dft_price is not None:
            self.price = self.sku.dft_price
            editted = True
        if self.srf is None:
            self.srf = self.sku.dft_srf * self.customer.dft_srf
            self.custom_srf = False
            editted = True
        if self.season_var is None:
            self.season_var = self.sku.dft_season_var
            editted = True
        if editted:
            self.save()

class SalesPeriod(models.Model):
    start_date = models.DateField()
    finish_date = models.DateField()
    customers = models.ManyToManyField(Customer, related_name='sales_periods', through='CustomerSalesPeriod')
    xl_id = models.IntegerField('Excel ID', default=-1)
    
    def str_simple_date(self):
        form = '%b-%y'
        return '%s to %s' % (self.start_date.strftime(form),
                             self.finish_date.strftime(form))
    
    def str_start(self):
        return self.start_date.strftime(settings.CUSTOM_DATE_FORMAT)
    
    def str_finish(self):
        return self.finish_date.strftime(settings.CUSTOM_DATE_FORMAT)
    
    def length_days(self):
        return (self.finish_date - self.start_date).days
    
    def __unicode__(self):
        return self.str_simple_date()

    class Meta:
        verbose_name_plural = 'Sales Periods'
        verbose_name = 'Sales Period'
        
class CustomerSalesPeriod(models.Model):
    customer = models.ForeignKey(Customer, related_name='c_sales_periods')
    period = models.ForeignKey(SalesPeriod, related_name='c_sales_periods')
    store_count = models.IntegerField(null = True)
    custom_store_count = models.BooleanField('Has Custom Store Count')
    
    def str_period(self):
        return self.period.str_simple_date()
    
    def __unicode__(self):
        s_count = ''
        if self.store_count is not None:
            s_count = '%d stores' % self.store_count
        return 'period from %s for %s, %s' % (self.period.start_date.strftime(settings.CUSTOM_DATE_FORMAT),
                                                      self.customer.name, s_count)
        
    def save(self, *args, **kwargs):
        resave = kwargs.pop('resave', False)
        super(CustomerSalesPeriod, self).save(*args, **kwargs)
        if resave:
            return
        if self.store_count is not None:
            if self.store_count != self.customer.dft_store_count:
                self.custom_store_count = True
                self.save(resave = True)
        if self.store_count is None and self.customer.dft_store_count is not None:
            self.store_count = self.customer.dft_store_count
            self.save(resave = True)

class SKUSales(models.Model):
    period = models.ForeignKey(CustomerSalesPeriod, related_name='sku_sales')
    csku = models.ForeignKey(CustomerSKUInfo, related_name='sku_sales', verbose_name="Customer SKU")
    sales = models.FloatField('Number of SKUs sold', default=0)
    xl_id = models.IntegerField('Excel ID', default=-1)
    income = models.DecimalField('Income from sales', max_digits=11, decimal_places=4, default = 0)
    cost = models.DecimalField('cost of SKUs sold', max_digits=11, decimal_places=4, default = 0)
    
    def sku_name(self):
        return self.csku.sku_name()
    
    def str_period(self):
        return self.period.period.str_simple_date()
    
    def __unicode__(self):
        return '%s sells %d at %s in %s' % (self.sku_name(), self.sales, self.csku.customer.name,  
                                            self.period.period.str_simple_date())
    
    class Meta:
        verbose_name_plural = 'SKU Sales'
        verbose_name = 'SKU Sales'