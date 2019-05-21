from django.contrib import admin
from .models import Item, Order, qty

admin.site.register(Item)
admin.site.register(Order)
admin.site.register(qty)