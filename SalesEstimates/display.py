import django_tables2 as tables
from django_tables2.utils import A
#from django_tables2_simplefilter import F
import SkeletalDisplay
import SalesEstimates.models as m
import HotDjango
from rest_framework import serializers

app_name='salesestimates'

class Manufacturer(SkeletalDisplay.ModelDisplay):
	model = m.Manufacturer
	index = -1
	attached_tables = [{'name':'OrderGroup', 'populate':'order_group', 'title':'Order Groups'}]
	
	class DjangoTable(tables.Table):
		name = tables.LinkColumn('display_item', args=[app_name, 'Manufacturer', A('pk')])
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass
	
	class HotTable(HotDjango.ModelSerialiser):
		class Meta:
			fields = ('id', 'name', 'description')

class CostLevel(SkeletalDisplay.ModelDisplay):
	model = m.CostLevel
	display = False
	
	class DjangoTable(tables.Table):
		order_quantity = tables.Column(verbose_name='Quantity')
		str_price = tables.Column(verbose_name='Price per unit')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			exclude = ('id', 'component', 'price')
	
	class HotTable(HotDjango.ModelSerialiser):
		class Meta:
			fields = ('id', 'order_group', 'order_quantity', 'price')

class OrderGroup(SkeletalDisplay.ModelDisplay):
	model = m.OrderGroup
	extra_funcs = [('Nominal Price', 'str_nominal_price')]
	attached_tables = [{'name':'CostLevel', 'populate':'costlevels', 'title':'Cost Levels'},
					{'name':'Component', 'populate':'components', 'title':'Components with this Order Group'}]
	
	index = 0
	
	class DjangoTable(tables.Table):
		name = tables.LinkColumn('display_item', args=[app_name, 'OrderGroup', A('pk')])
		manufacturer = tables.Column(verbose_name='Manufacturer')
		str_nominal_price = tables.Column(verbose_name='Nominal Price')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			exclude = ('id', 'description', 'nominal_price')
	
	related_tables = {'costlevels': CostLevel}
	class HotTable(HotDjango.ModelSerialiser):
		manufacturer = HotDjango.IDNameSerialiser(m.Manufacturer)
		class Meta:
			fields = ('id', 'name', 'description', 'comment', 'minimum_order', 'lead_time', 'manufacturer', 'costlevels')

class Component(SkeletalDisplay.ModelDisplay):
	model = m.Component
	extra_funcs = [('Nominal Price', 'str_nominal_price'), ('Manufacturer', 'get_manufacturer')]
	attached_tables = [{'name':'Assembly', 'populate':'assemblies', 'title':'Assemblies Using this Component'}]
	index = 1
	
	class DjangoTable(tables.Table):
		name = tables.LinkColumn('display_item', args=[app_name, 'Component', A('pk')])
		str_nominal_price = tables.Column(verbose_name='Nominal Price')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			exclude = ('id', 'description', 'nominal_price', 'xl_id')
	
	class HotTable(HotDjango.ModelSerialiser):
		order_group = HotDjango.IDNameSerialiser(m.OrderGroup)
		class Meta:
			fields = ('id', 'name', 'description', 'comment', 'order_group')

class Assembly(SkeletalDisplay.ModelDisplay):
	model = m.Assembly
	extra_funcs = [('Nominal Raw Cost', 'str_nominal_raw_cost'), ('Components', 'component_count')]
	attached_tables = [{'name':'Component', 'populate':'components', 'title':'Components'}]
	index = 2
	
	class DjangoTable(tables.Table):
		name = tables.LinkColumn('display_item', args=[app_name, 'Assembly', A('pk')])
		component_count = tables.Column(verbose_name='Components')
		str_nominal_raw_cost = tables.Column(verbose_name='Nominal Cost')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			exclude = ('id', 'description')
	
	class HotTable(HotDjango.ModelSerialiser):
		components = HotDjango.IDNameSerialiser(m.Component, many=True)
		class Meta:
			fields = ('id', 'name', 'description', 'comment', 'size', 'components')

class SKUGroup(SkeletalDisplay.ModelDisplay):
	model = m.SKUGroup
	index = 2.5
	
	class DjangoTable(tables.Table):
		name = tables.LinkColumn('display_item', args=[app_name, 'SKUGroup', A('pk')])
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass
	
	class HotTable(HotDjango.ModelSerialiser):
		class Meta:
			fields = ('id', 'name', 'description', 'comment')
			
class MonthSerialiser(serializers.WritableField):
	read_only = False
	def __init__(self, *args, **kwargs):
		super(MonthSerialiser, self).__init__(*args, **kwargs)
	def to_native(self, item):
		return next(choice[1] for choice in m.MonthVariation.MONTHS if choice[0] == item)
	def from_native(self, item):
		return next(choice[0] for choice in m.MonthVariation.MONTHS if choice[1] == item)
class MonthVariation(SkeletalDisplay.ModelDisplay):
	model = m.MonthVariation
	display = False
	
	class DjangoTable(tables.Table):
		get_month_display = tables.Column()
		srf = tables.Column(verbose_name='Sales Rate Factor')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass
	
	class HotTable(HotDjango.ModelSerialiser):
		month = MonthSerialiser()
		class Meta:
			fields = ('id', 'season_var', 'month', 'srf')
			
class SeasonalVariation(SkeletalDisplay.ModelDisplay):
	model = m.SeasonalVariation
	extra_funcs=[('Months', 'month_count')]
	attached_tables = [{'name':'MonthVariation', 'populate':'months', 'title':'Variation Months'}]
	index = 2.75
	
	class DjangoTable(tables.Table):
		name = tables.LinkColumn('display_item', args=[app_name, 'SeasonalVariation', A('pk')])
		month_count = tables.Column(verbose_name='Variation Months')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass
		
	related_tables = {'months': MonthVariation}
	class HotTable(HotDjango.ModelSerialiser):
		class Meta:
			fields = ('id', 'name', 'description', 'comment', 'months')
	
class SKU(SkeletalDisplay.ModelDisplay):
	model = m.SKU
	extra_funcs=[('Assemblies', 'assembly_count')]
	attached_tables = [{'name':'Assembly', 'populate':'assemblies', 'title':'Included Assemblies'}]
	index = 3
	
	class DjangoTable(tables.Table):
		name = tables.LinkColumn('display_item', args=[app_name, 'SKU', A('pk')])
		assembly_count = tables.Column(verbose_name='Assemblies')
		str_dft_price = tables.Column(verbose_name='Default Price')
		str_nominal_raw_cost = tables.Column(verbose_name='Nominal Raw Cost')
		group = tables.Column(verbose_name='Group')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			exclude = ('id', 'description', 'dft_price')
	
	class HotTable(HotDjango.ModelSerialiser):
		group = HotDjango.IDNameSerialiser(m.SKUGroup)
		assemblies = HotDjango.IDNameSerialiser(m.Assembly, many=True)
		dft_season_var = HotDjango.IDNameSerialiser(m.SeasonalVariation)
		class Meta:
			fields = ('id', 'name', 'description', 'comment', 'dft_price', 'dft_srf', 'dft_season_var', 'group', 'assemblies')

class Customer(SkeletalDisplay.ModelDisplay):
	model = m.Customer
	extra_funcs= [('SKUs', 'sku_count')]
	attached_tables = [{'name':'CustomerSKUInfo', 'table': 'Table2', 'populate':'c_skus', 'title':'SKUs Sold'},
					{'name':'CustomerSalesPeriod', 'populate':'c_sales_periods', 'title':'Sales Periods'}]
	index = 4
	
	class DjangoTable(tables.Table):
		name = tables.LinkColumn('display_item', args=[app_name, 'Customer', A('pk')])
		sku_count = tables.Column(verbose_name='SKUs')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			exclude = ('id', 'description')
		
	class HotTable(HotDjango.ModelSerialiser):
		skus = HotDjango.IDNameSerialiser(m.SKU, many=True)
		class Meta:
			fields = ('id', 'name', 'description', 'comment', 'dft_srf', 'skus')

class CustomerSKUInfo(SkeletalDisplay.ModelDisplay):
	model = m.CustomerSKUInfo
	index = 5
	attached_tables = [{'name':'SKUSales', 'table':'Table2', 'populate':'sku_sales', 'title':'SKU Sales Estimates'}]
	
	class DjangoTable(tables.Table):
		customer_name = tables.LinkColumn('display_item', args=[app_name, 'CustomerSKUInfo', A('pk')], verbose_name='Customer')
		xl_id = tables.Column(verbose_name='Excel ID')
		sku_name = tables.Column(verbose_name='SKU')
		str_price = tables.Column(verbose_name='Price')
		srf = tables.Column(verbose_name='Sale Rate')
		
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass
	
	class Table2(tables.Table):
		sku_name = tables.LinkColumn('display_item', args=[app_name, 'SKU', A('sku.pk')], verbose_name='SKU')
		str_price = tables.Column(verbose_name='Price')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass
		
	class HotTable(HotDjango.ModelSerialiser):
		sku = HotDjango.IDNameSerialiser(m.SKU)
		customer = HotDjango.IDNameSerialiser(m.Customer)
		season_var = HotDjango.IDNameSerialiser(m.SeasonalVariation)
		class Meta:
			fields = ('id', 'sku', 'customer', 'season_var', 'price', 'srf')

class SalesPeriod(SkeletalDisplay.ModelDisplay):
	model = m.SalesPeriod
	extra_funcs= [('Period', 'str_simple_date')]
	attached_tables = [{'name':'CustomerSalesPeriod', 'table': 'Table2', 'populate':'c_sales_periods', 'title':'Customers'}]
	index = 6
	
	class DjangoTable(tables.Table):
		str_simple_date = tables.LinkColumn('display_item', args=[app_name, 'SalesPeriod', A('pk')],
									verbose_name='Period')
		xl_id = tables.Column(verbose_name='Excel ID')
		length_days = tables.Column(verbose_name='Length in Days')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass

class CustomerSalesPeriod(SkeletalDisplay.ModelDisplay):
	model = m.CustomerSalesPeriod
	display = False
	attached_tables = [{'name':'SKUSales', 'populate':'sku_sales', 'title':'SKU Sales Estimates'}]
	
	class DjangoTable(tables.Table):
		str_period = tables.LinkColumn('display_item', args=[app_name, 'CustomerSalesPeriod', A('pk')],
									verbose_name='Sales Period')
		store_count = tables.Column(verbose_name='Store Count')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass
	
	class Table2(tables.Table):
		customer = tables.LinkColumn('display_item', args=[app_name, 'CustomerSalesPeriod', A('pk')],
									verbose_name='Customer')
		store_count = tables.Column(verbose_name='Store Count')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass

class SKUSales(SkeletalDisplay.ModelDisplay):
	model = m.SKUSales
	display = False
	
	class DjangoTable(tables.Table):
		sku_name = tables.LinkColumn('display_item', args=[app_name, 'SKUSales', A('pk')])
		sales = tables.Column(verbose_name='Number of Sales')
		cost = tables.Column(verbose_name='Cost of Sales')
		income = tables.Column(verbose_name='Income from Sales')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass
	
	class Table2(tables.Table):
		str_period = tables.LinkColumn('display_item', args=[app_name, 'SKUSales', A('pk')], verbose_name='Period')
		sales = tables.Column(verbose_name='Number of Sales')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass