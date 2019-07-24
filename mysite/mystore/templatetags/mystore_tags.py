from django import template

from ..models import Institution, Item, Order, Payments

register = template.Library()

@register.simple_tag
def total_col():
    return Institution.objects.all()

@register.inclusion_tag('mystore/college_list.html')
def all_institutions():
    all_inst = Institution.objects.all()
    return {'all_inst': all_inst}

@register.inclusion_tag('mystore/size_list.html')
def all_sizes():
    sizes = Item.objects.order_by('size').values_list('size', flat=True).distinct()
    return {'sizes': sizes}

@register.inclusion_tag('mystore/product_list.html')
def all_products():
    products = Item.objects.order_by('name').values_list('name', flat=True).distinct()
    return {'products': products}

@register.inclusion_tag('mystore/payment_list.html')
def all_payments(id=0):
    order = Order.objects.filter(id=id)
    payment = Payments.objects.filter(order=order)
    return {'payment': payment}