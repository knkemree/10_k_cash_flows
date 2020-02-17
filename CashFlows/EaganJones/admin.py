from django.contrib import admin
from EaganJones.models import Companies, UserProfile


# Register your models here.

class CompaniesAdmin(admin.ModelAdmin):
    list_display = ['companyname', 'cik', 'primarysymbol','created_at' ]
    list_filter = ['companyname', 'cik', 'primarysymbol']
    search_fields = ('companyname', 'cik', 'primarysymbol')
    list_display_links = ['primarysymbol', 'companyname', ]


admin.site.register(Companies, CompaniesAdmin)
admin.site.register(UserProfile)