from django import forms
from .models import Order, Item
from django.forms.widgets import CheckboxSelectMultiple

class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('order', 'client', 'added_by')

class SelForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('items',)

    def __init__(self, *args, **kwargs):
        super(SelForm, self).__init__(*args, **kwargs)

        self.fields["items"].widget = CheckboxSelectMultiple()
        self.fields["items"].queryset = Item.objects.all()
