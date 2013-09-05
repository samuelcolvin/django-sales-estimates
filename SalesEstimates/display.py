import django_tables2 as tables
from django_tables2.utils import A
#from django_tables2_simplefilter import F
import SkeletalDisplay
import SalesEstimates.models as m

class OrderGroup(SkeletalDisplay.ModelDisplay):
	extra_funcs=[('Nominal Price','str_nominal_price')]
	attached_tables = [{'name':'CostLevel', 'populate':'costlevels', 'title':'Cost Levels'},
					{'name':'Component', 'populate':'components', 'title':'Components with this Order Group'}]
	index = 0
	
	class Table(tables.Table):
		name = tables.LinkColumn('display_item', args=['SalesEstimates', 'OrderGroup', A('pk')])
		str_nominal_price = tables.Column(verbose_name='Nominal Price')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			model = m.OrderGroup
			exclude = ('id', 'description', 'nominal_price')

class CostLevel(SkeletalDisplay.ModelDisplay):
	extra_funcs=[]
	display = False
	
	class Table(tables.Table):
		str_price = tables.Column(verbose_name='Price per unit')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			model = m.CostLevel
			exclude = ('id', 'component', 'price')

class Component(SkeletalDisplay.ModelDisplay):
	extra_funcs=[('Nominal Price','str_nominal_price')]
	attached_tables = [{'name':'Assembly', 'populate':'assemblies', 'title':'Assemblies Using this Component'}]
	index = 1
	
	class Table(tables.Table):
		name = tables.LinkColumn('display_item', args=['SalesEstimates', 'Component', A('pk')])
		str_nominal_price = tables.Column(verbose_name='Nominal Price')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			model = m.Component
			exclude = ('id', 'description', 'nominal_price', 'xl_id')

class Assembly(SkeletalDisplay.ModelDisplay):
	extra_funcs=[('Nominal Raw Cost','str_nominal_raw_cost'), ('Components', 'component_count')]
	attached_tables = [{'name':'Component', 'populate':'components', 'title':'Components'}]
	index = 2
	
	class Table(tables.Table):
		name = tables.LinkColumn('display_item', args=['SalesEstimates', 'Assembly', A('pk')])
		component_count = tables.Column(verbose_name='Components')
		str_nominal_raw_cost = tables.Column(verbose_name='Nominal Cost')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			model = m.Assembly
			exclude = ('id', 'description')

class SKU(SkeletalDisplay.ModelDisplay):
	extra_funcs=[('Assemblies', 'assembly_count')]
	attached_tables = [{'name':'Assembly', 'populate':'assemblies', 'title':'Included Assemblies'}]
	index = 3
	
	class Table(tables.Table):
		name = tables.LinkColumn('display_item', args=['SalesEstimates', 'SKU', A('pk')])
		assembly_count = tables.Column(verbose_name='Assemblies')
		str_dft_price = tables.Column(verbose_name='Default Price')
		str_nominal_raw_cost = tables.Column(verbose_name='Nominal Raw Cost')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			model = m.SKU
			exclude = ('id', 'description', 'dft_price')

class Customer(SkeletalDisplay.ModelDisplay):
	extra_funcs=[('SKUs', 'sku_count')]
	attached_tables = [{'name':'CustomerSKU', 'table': 'Table2', 'populate':'c_skus', 'title':'SKUs Sold'},
					{'name':'CustomerSalesPeriod', 'populate':'c_sales_periods', 'title':'Sales Periods'}]
	index = 4
	
	class Table(tables.Table):
		name = tables.LinkColumn('display_item', args=['SalesEstimates', 'Customer', A('pk')])
		sku_count = tables.Column(verbose_name='SKUs')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			model = m.Customer
			exclude = ('id', 'description')

class SalesPeriod(SkeletalDisplay.ModelDisplay):
	extra_funcs=[('Period', 'str_simple_date')]
	attached_tables = [{'name':'CustomerSalesPeriod', 'table': 'Table2', 'populate':'c_sales_periods', 'title':'Customers'}]
	index = 6
	
	class Table(tables.Table):
		str_simple_date = tables.LinkColumn('display_item', args=['SalesEstimates', 'SalesPeriod', A('pk')],
									verbose_name='Period')
		xl_id = tables.Column(verbose_name='Excel ID')
		length_days = tables.Column(verbose_name='Length in Days')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass

class CustomerSKU(SkeletalDisplay.ModelDisplay):
	index = 5
	attached_tables = [{'name':'SKUSales', 'table':'Table2', 'populate':'sku_sale', 'title':'SKU Sales Estimates'}]
	
	class Table(tables.Table):
		customer_name = tables.LinkColumn('display_item', args=['SalesEstimates', 'CustomerSKU', A('pk')], verbose_name='Customer')
		xl_id = tables.Column(verbose_name='Excel ID')
		sku_name = tables.Column(verbose_name='SKU')
		str_price = tables.Column(verbose_name='Price')
		sale_rate = tables.Column(verbose_name='Sale Rate')
		
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass
	
	class Table2(tables.Table):
		sku_name = tables.LinkColumn('display_item', args=['SalesEstimates', 'SKU', A('sku.pk')], verbose_name='SKU')
		str_price = tables.Column(verbose_name='Price')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass

class CustomerSalesPeriod(SkeletalDisplay.ModelDisplay):
	display = False
	attached_tables = [{'name':'SKUSales', 'populate':'sku_sales', 'title':'SKU Sales Estimates'}]
	
	class Table(tables.Table):
		str_period = tables.LinkColumn('display_item', args=['SalesEstimates', 'CustomerSalesPeriod', A('pk')],
									verbose_name='Sales Period')
		store_count = tables.Column(verbose_name='Store Count')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass
	
	class Table2(tables.Table):
		customer = tables.LinkColumn('display_item', args=['SalesEstimates', 'CustomerSalesPeriod', A('pk')],
									verbose_name='Customer')
		store_count = tables.Column(verbose_name='Store Count')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass

class SKUSales(SkeletalDisplay.ModelDisplay):
	display = False
	
	class Table(tables.Table):
		sku_name = tables.LinkColumn('display_item', args=['SalesEstimates', 'SKUSales', A('pk')])
		sales = tables.Column(verbose_name='Number of Sales')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass
	
	class Table2(tables.Table):
		str_period = tables.LinkColumn('display_item', args=['SalesEstimates', 'SKUSales', A('pk')], verbose_name='Period')
		sales = tables.Column(verbose_name='Number of Sales')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass