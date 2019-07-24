from django.contrib import admin

from .models import Item, Order, Institution, Client, Payments


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
                    'quantity', 'prod_cost', 'quantity_ordered')
    prepopulated_fields = {'code': ('name', 'size','institution')}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'client','total', 'paid',
                    'discount', 'debt', 'created', 'due_date')

@admin.register(Payments)
class PaymentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'created')
