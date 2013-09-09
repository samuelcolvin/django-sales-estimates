from django.db import models
import settings
from datetime import datetime as dtdt

def content_file_name(instance, filename):
    now = dtdt.now().strftime(settings.CUSTOM_SHORT_DT_FORMAT)
    return 'excel_files/excel_upload_%s.xlsx' % now

class ExcelFiles(models.Model):
    xlfile = models.FileField(upload_to=content_file_name)