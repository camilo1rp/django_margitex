from django.contrib import admin
from .models import Item, Order, Qty, Institution

admin.site.register(Item)
admin.site.register(Order)
admin.site.register(Institution)
admin.site.register(Qty)