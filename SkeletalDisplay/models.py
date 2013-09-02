from django.db import models

class UserSetting(models.Model):
    key = models.CharField(unique=True, max_length=200)
    value = models.CharField(max_length=200)

    def __unicode__(self):
        return 'Setting: %s = %s' % (self.key, self.value)