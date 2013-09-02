from django.template import RequestContext
from django.shortcuts import render_to_response

from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str

from datetime import datetime
import settings

import markdown2, base64, json

from django.db import models

from django_tables2 import RequestConfig

import user_settings

import SkeletalDisplay

from pprint import pprint

def index(request):
	page_gen = PageGenerator(request)
	return page_gen.index()

def display_model(request, app_name, model_name):
	page_gen = PageGenerator(request)
	return page_gen.display_model(app_name, model_name)
	
def display_item(request, app_name, model_name, item_id):
	page_gen = PageGenerator(request)
	return page_gen.display_item(app_name, model_name, item_id)

class PageGenerator(object):
	def __init__(self, request):
		self._request = request
		pprint(self._request.session['crums'])
		self._apps = SkeletalDisplay.get_display_apps()
	
	def _set_model(self, app_name, model_name):
		self._disp_model = self._find_model(app_name, model_name)
		self._plural_t = self._get_plural_name(self._disp_model)
		self._single_t = self._disp_model.model._meta.verbose_name.title()
		
	def index(self):
		content = {'display_apps': SkeletalDisplay.json_apps(self._apps), 'page_menu': ()}
		return self._base(self._request, 'Market Trace', content, 'index.html')
	
	def display_model(self, app_name, model_name):
		self._set_model(app_name, model_name)
		links = ()
		self._request.session['crums'] = [{'app':app_name, 'disp_model':model_name, 'id': -1}]
		table = self._disp_model.Table(self._disp_model.model.objects.all())
		RequestConfig(self._request).configure(table)
		content = {'page_menu': links, 'table': table, 'crums': self._generate_crums()}
		return self._base(self._request, self._plural_t, content, 'model_display.html')
		
	def display_item(self, app_name, model_name, item_id):
		self._set_model(app_name, model_name)
		item = self._disp_model.model.objects.get(id = int(item_id))
		links = []
		self._request.session['crums'].append({'app':app_name, 'disp_model':model_name, 'id':int(item_id)})
		status_groups=[]
		title = '%s: %s' %  (self._single_t, str(item))
		status_groups.append({'title': title, 'fields': self._populate_fields(item, self._disp_model)})
		tbelow = self._populate_tables(item, self._disp_model)
		content = {'page_menu': links, 'status_groups': status_groups, 'crums': self._generate_crums(), 
			'tables_below': tbelow}
		return self._base(self._request, self._single_t, content, 'item_display.html')

	def _extract_crums(self, crums_raw):
		return json.loads(base64.b64decode(crums_raw))
	
	def _generate_crums(self):
		crums = []
		crums_up2now = []
		session_crums = self._request.session['crums']
		for crum in session_crums:
			dm = self._find_model(crum['app'], crum['disp_model'])
			if crum['id'] == -1:
				crums.append({'url': reverse('display_model', args=(crum['app'], crum['disp_model'])), 'name': self._get_plural_name(dm)})
			else:
				name = dm.model.objects.get(id=int(crum['id']))
				if len(crums_up2now) == 0:
					crums.append({'url': reverse('display_item', args=(crum['app'], crum['disp_model'], crum['id'])), 'name': name})
				else:
					crums.append({'url': reverse('display_item', args=(crum['app'], crum['disp_model'], crum['id'])), 'name': name})
			crums_up2now.append(crum)
		return crums
	
	def _cap(self, string):
		words = string.split(' ')
		for word in words:
			word = word.capitalize()
	
	def _find_model(self, app_name, model_name):
		try:
			return self._apps[app_name][model_name]
		except:
			raise Exception('ERROR: %s.%s not found' % (app_name, model_name))
		
	def _populate_fields(self, item, dm, exceptions=[]):
		item_fields=[]
		for field in dm.model._meta.fields:
			if field.name in exceptions:
				continue
			name = field.verbose_name
			value = self._convert_to_string(getattr(item, field.name), field.name)
			item_fields.append({'name': name, 'state': value })
		if hasattr(dm, 'extra_funcs'):
			for func in dm.extra_funcs:
				value = self._convert_to_string(getattr(item, func[1])(), func[0])
				item_fields.append({'name': func[0], 'state': value})
		return item_fields
	
	def _populate_tables(self, item, model):
		generated_tables = []
		if hasattr(model, 'attached_tables'):
			for tab in model.attached_tables:
				this_table={'title': tab['title']}
				if 'populate' in tab:
					popul = getattr(item, tab['populate']).all()
				else:
					popul = getattr(item,  tab['populate_func'])()
				this_table['renderable'] = self._apps[self._disp_model.app_parent][tab['name']].Table(popul)
				RequestConfig(self._request).configure(this_table['renderable'])
				generated_tables.append(this_table)

		return generated_tables
	
	def _convert_to_string(self, value, name):
		if value == None:
			return ''
		if isinstance(value, bool):
			if value:
				return u'\u2713'
			else:
				return u'\u2718'
		elif isinstance(value, long) or isinstance(value, int) or isinstance(value, float):
			return self._find_base(value)
		elif isinstance(value, datetime):
			return value.strftime(settings.CUSTOM_DT_FORMAT)
		elif isinstance(value, models.Model):
			model_name = value.__class__.__name__
			app_name = value.__module__.replace('.models', '')
			return '<a href="%s">%s</a>' % (reverse('display_item', args=[app_name, model_name, value.id]), str(value))
		else:
			if name == 'index':
				if value.startswith('    '):
					value = value[2:]
					value = value.replace('\n    ', '\n  ')
				value = markdown2.markdown(value)
			elif name in ['raw', 'log']:
				value = '<textarea>%s</textarea>' % value
			return smart_str(value)
	
	def _find_base(self, value):
		if value > 1e12:
			v = value/1e12
			return '%0.3f T' % v
		elif value > 1e9:
			v = value/1e9
			return '%0.3f B' % v
		elif value > 1e6:
			v = value/1e6
			return '%0.3f M' % v
		elif value > 1e3:
			v = value/1e3
			return '%0.3f K' % v
		elif isinstance(value, float):
			return '%0.2f' % value
		else:
			return '%d' % value
	
	def _base(self, request, title, content, template):
		top_menu = [{'url': reverse('admin:index'), 'name': 'Admin'}]
				
				# [{'url': reverse('test_url'), 'name': 'Test URL'},
				#{'url': reverse('add_trace'), 'name': 'Add Trace'},
				#{'url': reverse('admin_a_model', args=['index']), 'name': 'Admin'}]
		main_menu=[]
		active = None
		if hasattr(self, '_disp_model'): active = self._disp_model.__name__
		for app_name in self._apps:
			for model_name in self._apps[app_name]:
				model = self._apps[app_name][model_name]
				if model.display:
					cls = ''
					if model_name == active: cls = 'active'
					main_menu.append({'url': reverse('display_model', args=[app_name, model_name]), 
									'name': self._get_plural_name(model), 'class': cls, 'index': model.index})
		main_menu = sorted(main_menu, key=lambda d: d['index'])
		site_title = user_settings.get_value('site_title')
		content.update({'top_menu': top_menu, 'site_title': site_title, 'title': title, 'menu': main_menu, 'content_template': template})
		return render_to_response('base.html', content, context_instance=RequestContext(request))

	def _get_plural_name(self, dm):
		return dm.model._meta.verbose_name_plural.title()