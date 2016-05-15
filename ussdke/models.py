from django.utils import timezone

from django.db import models


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
    icon=models.ImageField(upload_to='images/icons', default='images/icons/default.jpg')
    website=models.URLField()

    def __str__(self):
        return self.name

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

    def __str__(self):
        return self.code.value

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(USSD, self).save(*args, **kwargs)