from django.db import models

class ExcelFiles(models.Model):
    xlfile = models.FileField(upload_to='excel_files/%Y_%m_%d')