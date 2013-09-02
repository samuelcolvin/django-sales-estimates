import django_tables2 as tables
from django_tables2.utils import A
#from django_tables2_simplefilter import F
import json, base64
import SkeletalDisplay
import SalesEstimates.models as m

class Component(SkeletalDisplay.ModelDisplay):
	extra_funcs=[('Nominal Price','str_nominal_price')]
	attached_tables = [{'name':'CostLevel', 'populate':'costlevels', 'title':'Cost Levels'},
					{'name':'Assembly', 'populate':'assemblies', 'title':'Assemblies Using this Component'}]
	index = 1
	
	class Table(tables.Table):
		name = tables.LinkColumn('display_item', args=['SalesEstimates', 'Component', A('pk')])
		str_nominal_price = tables.Column(verbose_name='Nominal Price')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			model = m.Component
			exclude = ('id', 'description', 'nominal_price')

class CostLevel(SkeletalDisplay.ModelDisplay):
	extra_funcs=[]
	display = False
	
	class Table(tables.Table):
		str_price = tables.Column(verbose_name='Price per unit')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			model = m.CostLevel
			exclude = ('id', 'component', 'price')


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
		component_count = tables.Column(verbose_name='Components')
		str_nominal_raw_cost = tables.Column(verbose_name='Nominal Cost')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			model = m.SKU
			exclude = ('id', 'description')

class Customer(SkeletalDisplay.ModelDisplay):
	extra_funcs=[('SKUs', 'sku_count')]
	attached_tables = [{'name':'CustomerSKU', 'populate':'c_skus', 'title':'SKUs Sold'}]
	index = 4
	
	class Table(tables.Table):
		name = tables.LinkColumn('display_item', args=['SalesEstimates', 'Customer', A('pk')])
		sku_count = tables.Column(verbose_name='SKUs')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			model = m.Customer
			exclude = ('id', 'description')

class CustomerSKU(SkeletalDisplay.ModelDisplay):
	extra_funcs=[]
	display = False
	
	class Table(tables.Table):
		sku_name = tables.LinkColumn('display_item', args=['SalesEstimates', 'SKU', A('sku.pk')])
		str_price = tables.Column(verbose_name='Price')
		class Meta(SkeletalDisplay.ModelDisplayMeta):
			pass