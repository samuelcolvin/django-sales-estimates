from django import forms

import ExcelImportExport.models as m
import ExcelImportExport.ImportExport as imex
import SkeletalDisplay
from SkeletalDisplay.views import base as skeletal_base

class ExcelUploadForm(forms.Form):
    xlfile = forms.FileField(
        label='Select Excel (xlsx) File to Upload',
        help_text='should be in standard format for this system'
    )

def display(request):
    # Handle file upload
    log = None
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            newfile = m.ExcelFiles(xlfile = request.FILES['xlfile'], source='UP')
            newfile.save()
            fname = newfile.xlfile.path
            log = imex.perform_import(fname, True)
    else:
        form = ExcelUploadForm()
    return (form, log)

def upload(request):
    apps = SkeletalDisplay.get_display_apps()
    (upload_form, log) = display(request)
    content = {'upload_form': upload_form, 'log': log}
    return skeletal_base(request, 'Import Files', content, 'upload.html', apps)

def download(request):
    apps = SkeletalDisplay.get_display_apps()
    (url, log) = imex.perform_export()
    content = {'download_url': url, 'log': log}
    return skeletal_base(request, 'Import Files', content, 'download.html', apps)