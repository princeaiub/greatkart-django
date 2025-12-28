from django.contrib import admin
from .models import Superuser, Staffuser, Generaluser

# Register your models here.

admin.site.register([Superuser,Staffuser,Generaluser])