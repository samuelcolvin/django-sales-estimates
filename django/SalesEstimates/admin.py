from django.contrib import admin
import SalesEstimates.models as m

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'results_status')
    
admin.site.register(m.Company, CompanyAdmin)

class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    
admin.site.register(m.Manufacturer, ManufacturerAdmin)
    
class CostlevelsAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_group', 'order_quantity', 'price')
    
admin.site.register(m.CostLevel, CostlevelsAdmin)

class CostLevelInline(admin.TabularInline):
    model = m.CostLevel
    extra = 5
    
class OrderGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'minimum_order', 'str_nominal_price')
    inlines = [CostLevelInline]
    exclude = ('nominal_price',)
    
admin.site.register(m.OrderGroup, OrderGroupAdmin)

class ComponentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'str_nominal_price')
    
admin.site.register(m.Component, ComponentAdmin)

class AssyComponentInline(admin.TabularInline):
    model = m.AssyComponent
    extra = 5

class AssemblyAdmin(admin.ModelAdmin):
    inlines = [AssyComponentInline]
    list_display = ('id', 'name', 'nominal_raw_cost', 'component_count')

admin.site.register(m.Assembly, AssemblyAdmin)

class SKUGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

admin.site.register(m.SKUGroup, SKUGroupAdmin)

class SKUAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'dft_price', 'nominal_raw_cost', 'assembly_count')

admin.site.register(m.SKU, SKUAdmin)

class MonthVariationInline(admin.TabularInline):
    model = m.MonthVariation
    extra = 5

class SeasonalVariationAdmin(admin.ModelAdmin):
    inlines = [MonthVariationInline]
    list_display = ('id', 'name', 'month_count')
    
admin.site.register(m.SeasonalVariation, SeasonalVariationAdmin)

class PromotionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'srf', 'price_ratio')
    
admin.site.register(m.Promotion, PromotionAdmin)

class CustomerSKUInfoInline(admin.TabularInline):
    model = m.CustomerSKUInfo
    extra = 5

class CustomerSalesPeriodInline(admin.TabularInline):
    model = m.CustomerSalesPeriod
    extra = 5

class CustomerAdmin(admin.ModelAdmin):
    inlines = [CustomerSKUInfoInline, CustomerSalesPeriodInline]
    list_display = ('id', 'name', 'sku_count')
    
admin.site.register(m.Customer, CustomerAdmin)

class CustomerSKUInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'sku', 'customer', 'str_price', 'srf', 'season_var')
    
admin.site.register(m.CustomerSKUInfo, CustomerSKUInfoAdmin)

class CustomerSalesPeriodInline(admin.TabularInline):
    model = m.CustomerSalesPeriod
    extra = 5

class SalesPeriodAdmin(admin.ModelAdmin):
    inlines = [CustomerSalesPeriodInline]
    list_display = ('id', 'start_date', 'finish_date')
    
admin.site.register(m.SalesPeriod, SalesPeriodAdmin)

class SKUSalesInline(admin.TabularInline):
    model = m.SKUSales
    extra = 5

class CustomerSalesPeriodAdmin(admin.ModelAdmin):
    inlines = [SKUSalesInline]
    list_filter = ('customer', 'custom_store_count')
    list_display = ('id', 'period', 'customer', 'store_count', 'custom_store_count')
    
admin.site.register(m.CustomerSalesPeriod, CustomerSalesPeriodAdmin)

class SKUSalesAdmin(admin.ModelAdmin):
    list_display = ('id', 'csku', 'period', 'sales')
    
admin.site.register(m.SKUSales, SKUSalesAdmin)

class DemandInline(admin.TabularInline):
    model = m.Demand
    extra = 5

class OrderAdmin(admin.ModelAdmin):
    inlines = [DemandInline]
    list_display = ('id', 'place_date', 'order_group', 'demand_count', 'items', 'str_cost')
    
admin.site.register(m.Order, OrderAdmin)

class DemandAdmin(admin.ModelAdmin):
    list_display = ('id', 'required_date', 'lead_time_total', 'str_simple_date', 'order_group', 'items')
    
admin.site.register(m.Demand, DemandAdmin)
    
