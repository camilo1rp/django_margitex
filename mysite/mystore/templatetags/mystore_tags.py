from django import template
from ..models import Institution, Item
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
