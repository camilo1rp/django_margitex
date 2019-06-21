from django.contrib import admin
from .models import Item, Order, Qty, Institution, Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_slug')
    prepopulated_fields = {'name_slug':('name',)}

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'size', 'institution', 'code', 'price',
                    'quantity', 'created', 'updated')
    prepopulated_fields = {'code': ('name', 'size','institution')}
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'client','total', 'paid',
                    'discount', 'debt', 'created', 'due_date')
#admin.site.register(Item)
#admin.site.register(Order)
#admin.site.register(Institution)
admin.site.register(Qty)