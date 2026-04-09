from django.contrib import admin # type: ignore
from .models import Servicios,Promocion

admin.site.register(Servicios)
admin.site.register(Promocion)  

# Register your models here.
