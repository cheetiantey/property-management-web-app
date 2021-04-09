from django.contrib import admin
from .models import User, Email, Unit, Tenant, Maintenance, Document

# Register your models here.
admin.site.register(User) 
admin.site.register(Email) 
admin.site.register(Unit)
admin.site.register(Tenant)
admin.site.register(Maintenance)
admin.site.register(Document)