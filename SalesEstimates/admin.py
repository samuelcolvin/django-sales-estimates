from django.contrib import admin
import SalesEstimates.models as m

class CostLevelInline(admin.TabularInline):
    model = m.CostLevel
    extra = 5

class ComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'minimum_order', 'nominal_price')
    inlines = [CostLevelInline]
    exclude = ('nominal_price',)
    
admin.site.register(m.Component, ComponentAdmin)

class ComponentInline(admin.TabularInline):
    model = m.Assembly.components.through
    extra = 5

class AssemblyAdmin(admin.ModelAdmin):
    inlines = [ComponentInline]
    list_display = ('name', 'nominal_raw_cost', 'component_count')
    exclude = ('components',)

admin.site.register(m.Assembly, AssemblyAdmin)

class SKUAdmin(admin.ModelAdmin):
    list_display = ('name', 'dft_price', 'nominal_raw_cost', 'assembly_count')

admin.site.register(m.SKU, SKUAdmin)

class CustomerSKUInline(admin.TabularInline):
    model = m.CustomerSKU
    extra = 5

class CustomerAdmin(admin.ModelAdmin):
    inlines = [CustomerSKUInline]
    list_display = ('name', 'sku_count')
    
admin.site.register(m.Customer, CustomerAdmin)

class CustomerSalesPeriodInline(admin.TabularInline):
    model = m.CustomerSalesPeriod
    extra = 5

class SalesPeriodAdmin(admin.ModelAdmin):
    inlines = [CustomerSalesPeriodInline]
    list_display = ('start_date', 'finish_date')
    
admin.site.register(m.SalesPeriod, SalesPeriodAdmin)

class SKUSalesInline(admin.TabularInline):
    model = m.SKUSales
    extra = 5

class CustomerSalesPeriodAdmin(admin.ModelAdmin):
    inlines = [SKUSalesInline]
    list_display = ('period', 'customer', 'store_count')
    
admin.site.register(m.CustomerSalesPeriod, CustomerSalesPeriodAdmin)

class SKUSalesAdmin(admin.ModelAdmin):
    list_display = ('sku', 'period', 'sales')
    
admin.site.register(m.SKUSales, SKUSalesAdmin)

