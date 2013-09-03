from django.forms.models import modelform_factory
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from SkeletalDisplay.views import base

def add_item(request, app_name, model_name):
    model_editor = ModelEditor(request, app_name, model_name)
    return model_editor.add_item()

def edit_item(request, app_name, model_name, item_id):
    model_editor = ModelEditor(request, app_name, model_name)
    return model_editor.edit_item(item_id)

def delete_item(request, app_name, model_name, item_id):
    model_editor = ModelEditor(request, app_name, model_name)
    return model_editor.delete_item(item_id)

class ModelEditor:
    def __init__(self, request, app_name, model_name):
        self._request = request
        self._app_name = app_name
        self._model_name = model_name
        self._get_form_model()
        self._content = {}
        self._content['message'] = ''
            
    def add_item(self):
        self._title = 'Add %s' % self._model.__name__
        if self._request.method == 'POST':
            self._main_form = self._form_metaclass(self._request.POST)
            return self._save()
        else:
            self._main_form = self._form_metaclass()
            return self._return_form()
        
    def edit_item(self, item_id):
        self._title = 'Edit %s' % self._model.__name__
        item = self._model.objects.get(id=int(item_id))
        if self._request.method == 'POST':
            self._main_form = self._form_metaclass(self._request.POST, instance=item)
            return self._save()
        else:
            self._main_form = self._form_metaclass(instance=item)
            return self._return_form()
    
    def delete_item(self, item_id):
        item = self._model.objects.get(id=int(item_id))
        item.delete()
        self._add_line('%s: %s deleted' % (self._model.__name__, item))
        return redirect(reverse('display_model', args=[self._app_name, self._model_name]))
    
    def _save(self): 
        item = self._main_form.save(commit=False)
        if self._main_form.is_valid():
            item.save()
            self._add_line('Model saved')
            self._request.session['message'] = self._content['message']
            return redirect(reverse('display_item', args=[self._app_name, self._model_name, item.id])) 
        else:
            self._add_line('Form not valid')
            if not self._trace_form.is_valid(): self._add_line('Trace form not valid')
            if not self._ss_formset.is_valid(): self._add_line('Specific source form not valid') 
            return self._return_form()
    
    def _return_form(self):
        self._content['main_form'] = self._main_form.as_p
        return base(self._request, self._title, self._content, 'add_edit.html')

    def _get_form_model(self):
        app_forms = __import__(self._app_name + '.forms')
        app_models = __import__(self._app_name + '.models')
        self._model = getattr(app_models.models, self._model_name)
        if hasattr(app_forms.forms, self._model_name):
            self._form_metaclass = getattr(app_forms.forms, self._model_name)
        else:
            self._form_metaclass = modelform_factory(self._model)
    
    def _add_line(self, line):
        self._content['message'] += '<p>%s</p>\n' % line