from django.db import models
import settings
from datetime import datetime as dtdt

def content_file_name(instance, filename):
    now = dtdt.now().strftime(settings.CUSTOM_SHORT_DT_FORMAT)
    return 'excel_files/excel_%s.xlsx' % now

class ExcelFiles(models.Model):
    source = models.CharField(max_length=2, choices=(('UP', 'File Uploaded'), ('DL', 'File Generated for Download')))
    xlfile = models.FileField(upload_to=content_file_name)