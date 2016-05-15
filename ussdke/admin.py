from django.contrib import admin
from ussdke.models import Company,USSD,Code
# Register your models here.


class USSDInline(admin.TabularInline):
    model = USSD
    fields = ['code','description','confirmed','last_confirmed',]
    extra = 0


class CodeAdmin(admin.ModelAdmin):
    extra = 1
    search_fields = ['value']
    #inlines = [USSDInline]


class USSDAdmin(admin.ModelAdmin):
    extra = 1
    search_fields = ['description']
    #inlines = [USSDInline]


class CompanyAdmin(admin.ModelAdmin):
    extra = 1
    list_filter = ['name']
    search_fields = ['name']
    inlines = [USSDInline]


admin.site.register(USSD,USSDAdmin)
admin.site.register(Code,CodeAdmin)
admin.site.register(Company,CompanyAdmin)