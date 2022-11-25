from django.contrib import admin

# Register your models here.
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from App.models import Logins, UtrUpdate


class LoginResource(resources.ModelResource):
    class Meta:
        model = Logins
        import_id_field = ('emp_id')


class LoginAdmin(ImportExportModelAdmin):
    list_display = ['emp_id', 'designation', 'personal_number']
    resource_class = LoginResource


admin.site.register(Logins, LoginAdmin)
admin.site.register(UtrUpdate)