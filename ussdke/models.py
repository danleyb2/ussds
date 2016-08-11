from django.utils import timezone

from django.db import models
from cloudinary.models import CloudinaryField
from django.core.urlresolvers import reverse

# Create your models here.



class Code(models.Model):
    value = models.CharField(max_length=100)
    is_template = models.BooleanField(default=False)

    def __str__(self):
        return self.value


class Company(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()
    #icon=models.ImageField(upload_to='images/icons', default='images/icons/default.jpg')
    icon = CloudinaryField('icon')
    website=models.URLField()
    isSuggestion = models.BooleanField(default=1)

    def __str__(self):
        return self.name

    def get_ussds_url(self):
        #return str(self.id)+'/ussds'
        return reverse('ussdke:api:companies:company:ussds',args=[str(self.id)]) # todo

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(Company, self).save(*args, **kwargs)


class USSD(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,related_name='ussds',related_query_name='ussd')
    code = models.ForeignKey(Code)
    description = models.TextField()
    confirmed = models.BooleanField(default=False)
    last_confirmed = models.DateTimeField()
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField()
    isSuggestion = models.BooleanField(default=1)

    def __str__(self):
        return self.code.value

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(USSD, self).save(*args, **kwargs)