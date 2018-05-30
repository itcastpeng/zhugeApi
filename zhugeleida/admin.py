from django.contrib import admin

from zhugeleida import models

# Register your models here.
admin.site.register(models.zgld_userprofile)
admin.site.register(models.zgld_role)
admin.site.register(models.zgld_accesslog)
admin.site.register(models.zgld_company)
admin.site.register(models.zgld_customer)
admin.site.register(models.zgld_photo)
admin.site.register(models.zgld_quanxian)
admin.site.register(models.zgld_information)
admin.site.register(models.zgld_tag)

