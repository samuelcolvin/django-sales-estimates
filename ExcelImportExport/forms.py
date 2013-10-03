from django import forms

import ExcelImportExport.models as m
import ExcelImportExport.ImportExport as imex
import SkeletalDisplay
import SkeletalDisplay.views_base as viewb
# import SalesEstimates.worker
# import settings, os
# from django.core.files import File
from django.shortcuts import render
from django.core.urlresolvers import reverse
import traceback

# def perform_export():
#     logger = SkeletalDisplay.Logger()
#     tmp_fname = 'tmp.xlsx'
#     if settings.ON_SERVER:
#         tmp_fname = os.path.join(settings.SITE_ROOT,  tmp_fname)
#     imex.WriteXl(tmp_fname, logger.addline)
#     f_tmp = open(tmp_fname, 'r')
#     file_mdl = imex.ExcelImportExport.models.ExcelFiles()
#     file_mdl.xlfile.save(tmp_fname, File(f_tmp))
#     file_mdl.source = 'DL'
#     file_mdl.save()
#     return (file_mdl.xlfile.url, logger.get_log())
# 
# def perform_import(fname, delete_first):
#     logger = SkeletalDisplay.Logger()
#     if delete_first:
#         SalesEstimates.worker.delete_before_upload(logger.addline)
#     imex.ReadXl(fname, logger.addline)
#     return logger.get_log()


class Export(viewb.TemplateBase):
    template_name = 'download.html'
    top_active = 'export'
    side_menu = False
    worker_funcs={'export': {'func': imex.perform_export, 'msg': 'Successfully Generated XLSX Export'},}
    
    def setup_context(self, **kw):
        super(Export, self).setup_context(**kw)
    
    def get_context_data(self, **kw):
        self._context['title'] = 'Generate Sales Estimates'
        self._context['page_menu'] = self.set_links()
        self.choose_func(kw)
        return self._context
    
    def set_links(self):
        links= []
        links.append({'url': reverse('export', kwargs={'command': 'export'}), 'name': 'Generate XLSX Export'})
        return links
        
    def choose_func(self, kw):
        if 'command' in kw:
            command = kw['command']
            if command in self.worker_funcs:
                self.do(**self.worker_funcs[command])
            else:
                self._context['errors'] = ['%s does not have function for command %s' % (self.__name__, command)]
            
    def do(self, func=None, msg=None):
        logger = SkeletalDisplay.Logger()
        try:
            self._context.update(func(logger.addline))
        except Exception, e:
            error_msg = 'ERROR: %s' % str(e)
            self._context['errors'] = [error_msg]
            print error_msg
            traceback.print_exc()
        else:
            self._context['success'] = [msg]
        finally:
            self._context['info'] = logger.get_log()

def download(request):
    context = imex.perform_export()
    context['title'] = 'Download Files'
    context.update(viewb.basic_context(request, 'download'))
    return render(request, 'download.html', context)

class ExcelUploadForm(forms.Form):
    xlfile = forms.FileField(
        label='Select Excel (xlsx) File to Upload',
        help_text='should be in standard format for this system'
    )

def display(request):
    fname = None
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            if not str(request.FILES['xlfile']).endswith('.xlsx'):
                form = ExcelUploadForm()
                return (form, 'File must be xlsx, not xls or any other format.')
            newfile = m.ExcelFiles(xlfile = request.FILES['xlfile'], source='UP')
            newfile.save()
            fname = newfile.xlfile.path
    else:
        form = ExcelUploadForm()
    return (form, fname)

def upload(request):
    content = {}
    (upload_form, fname) = display(request)
    content['upload_form'] = upload_form
    if fname != None:
        content.update(imex.perform_import(fname, True))
    
    content['title'] = 'Import Files'
    content.update(viewb.basic_context(request, 'upload'))
    return render(request, 'upload.html', content)