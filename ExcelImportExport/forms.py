from django import forms

import ExcelImportExport.models as m
import ExcelImportExport.ImportExport as imex
import SkeletalDisplay
import SkeletalDisplay.views_base as viewb
import SalesEstimates.worker
import settings, os
from django.core.files import File
from django.shortcuts import render

def perform_export():
    logger = SkeletalDisplay.Logger()
    tmp_fname = 'tmp.xlsx'
    if settings.ON_SERVER:
        tmp_fname = os.path.join(settings.SITE_ROOT,  tmp_fname)
    imex.WriteXl(tmp_fname, logger.addline)
    f_tmp = open(tmp_fname, 'r')
    file_mdl = imex.ExcelImportExport.models.ExcelFiles()
    file_mdl.xlfile.save(tmp_fname, File(f_tmp))
    file_mdl.source = 'DL'
    file_mdl.save()
    return (file_mdl.xlfile.url, logger.get_log())

def perform_import(fname, delete_first):
    logger = SkeletalDisplay.Logger()
    if delete_first:
        SalesEstimates.worker.delete_before_upload(logger.addline)
    imex.ReadXl(fname, logger.addline)
    return logger.get_log()


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

def download(request):
    content = imex.perform_export()
    content['title'] = 'Download Files'
    content.update(viewb.basic_context(request, 'download'))
    return render(request, 'download.html', content)