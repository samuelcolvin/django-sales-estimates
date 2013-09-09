from django import forms

import UploadedFiles.models as m
import SalesEstimates.ImportExport as imex
# import os, settings

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
            newfile = m.ExcelFiles(xlfile = request.FILES['xlfile'])
            newfile.save()
            fname = newfile.xlfile.path
            log = imex.perform_import(fname, True)
    else:
        form = ExcelUploadForm()
    return (form, log)