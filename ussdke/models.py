from django.utils import timezone

from django.db import models
from cloudinary.models import CloudinaryField
from django.core.urlresolvers import reverse
from django.contrib.auth.admin import User
# Create your models here.



class Code(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    value = models.CharField(max_length=100)
    is_template = models.BooleanField(default=False)

    def __str__(self):
        return self.value


class Company(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #icon=models.ImageField(upload_to='images/icons', default='images/icons/default.jpg')
    icon = CloudinaryField('icon')
    website=models.URLField()
    isSuggestion = models.BooleanField(default=1)

    def __str__(self):
        return self.name

    def stargazer(self, user):
        return CompanyStar.objects.filter(company=self, author=user).count()

    def get_ussds_url(self):
        #return str(self.id)+'/ussds'
        return reverse('ussdke:api:companies:company:ussds',args=[str(self.id)])



class USSD(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,related_name='ussds',related_query_name='ussd')
    code = models.ForeignKey(Code)
    description = models.TextField()
    confirmed = models.BooleanField(default=False)
    last_confirmed = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    isSuggestion = models.BooleanField(default=1)

    def __str__(self):
        return self.code.value

    def get_invalidation_list_url(self):
        return reverse('ussdke:api:ussds:ussd:invalidation:list', args=[str(self.id)])

    def invalidate(self,data):
        invalidation = Invalidation()
        invalidation.reason = data.get('reason')
        invalidation.ussd = self
        invalidation.save()
        return self



class CompanyStar(models.Model):
    company = models.ForeignKey(Company, related_name='stars')
    author = models.ForeignKey(User)
    created_date = models.DateTimeField(default=timezone.now)


class Invalidation(models.Model):
    reason = models.CharField(max_length=200,null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    checked = models.BooleanField(default=False)
    ussd = models.ForeignKey(USSD,null=False)

    def __str__(self):
        return self.reason
