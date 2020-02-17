import jsonfield
from django.conf import settings
from django.db import models
# Create your models here.
from django.urls import reverse


class Companies(models.Model):
    companyname = models.CharField(max_length=200, db_index=True, blank=True, null=True)
    table = models.TextField(blank=True, null=True)
    cik = models.IntegerField(db_index=True)
    primarysymbol = models.CharField(max_length=200, db_index=True,)
    markettier = models.CharField(max_length=200, blank=True, null=True)
    siccode = models.CharField(max_length=200, blank=True, null=True)
    sicdescription = models.CharField(max_length=200, blank=True, null=True)
    entityid = models.CharField(max_length=200, blank=True, null=True)
    primaryexchange = models.CharField(max_length=200, blank=True, null=True)
    marketoperator = models.CharField(max_length=200, blank=True, null=True)
    jsonnn = jsonfield.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.companyname

    class Meta:
        ordering = ('companyname','cik','primarysymbol')

    index_together = (('id', 'primarysymbol'),)


    def get_absolute_url(self):
        return reverse('EaganJones:company_detail',
                       args=[self.id, self.primarysymbol])

class UserProfile(models.Model):
    user =models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_scrape = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{}-{}".format(self.user, self.last_scrape)