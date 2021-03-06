from django import forms

from .models import Order, Qty, Client


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('client', 'added_by', 'order')
        labels = {'client': 'cliente',
                  'added_by':'agregado por'
                  }

class SelForm(forms.ModelForm):

    class Meta:
        model = Qty
        fields = ('item',)
        labels = {'item':'producto'}
    def __init__(self, *args, **kwargs):
        super(SelForm, self).__init__(*args, **kwargs)
        #self.fields["item"].widget = CheckboxSelectMultiple()
        self.fields['item'].empty_label = None
        
class ConfirmForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('paid', 'discount', 'due_date')


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    content = forms.CharField(required=False,
                                widget=forms.Textarea)

class SearchForm(forms.Form):
    pedido = forms.CharField()

class ClientSearchForm(forms.Form):
    buscador = forms.CharField()

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('name', 'email', 'phone')

class ItemSearchForm(forms.Form):
    producto = forms.CharField(required=False)