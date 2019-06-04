from django import forms
from .models import Order, Item, Qty, Institution
from django.forms.widgets import *

class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('order', 'client', 'added_by')
"""
class SelForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('items',)

    def __init__(self, *args, **kwargs):
        super(SelForm, self).__init__(*args, **kwargs)

        self.fields["items"].widget = CheckboxSelectMultiple()
        self.fields["items"].queryset = Item.objects.all()
"""
class SelForm(forms.ModelForm):

    class Meta:
        model = Qty
        fields = ('item',)
"""
    def __init__(self, institution = None, *args, **kwargs):
        super(SelForm, self).__init__(*args, **kwargs)

        if institution == None:
            # self.fields["item"].widget = CheckboxSelectMultiple()
            self.fields["item"].queryset = Item.objects.all()
        else:
            self.fields["item"].widget = CheckboxSelectMultiple()
            self.fields["item"].queryset = Item.objects.filter(institution=institution)
"""