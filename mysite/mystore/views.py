from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .forms import OrderForm, SelForm

from .models import Order, Item


class IndexView(generic.ListView):
    template_name = 'mystore/index.html'
    context_object_name = 'latest_order_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Order.objects.all()
"""
class DetailView(generic.DetailView):
    model = Order
    template_name = 'mystore/detail.html'

    def get_queryset(self):
        return Order.objects.all()
"""
def detail(request, order_id, item_rmv=None):
    order = get_object_or_404(Order, pk=order_id)
    order.items.remove(item_rmv)
    if request.method == 'POST':
        form = SelForm(request.POST or None, instance=order)
        order_items = order.items
        # An order was added
        if form.is_valid():
            new_items = form.save(commit=False)
            new_items.items.add(*form.cleaned_data['items'])
            new_items.save()
            return HttpResponseRedirect(reverse('mystore:detail', args=(order.id,)))
    else:
        form = SelForm()
    return render(request, 'mystore/detail.html', {'form': form,
                                                   'order': order},)


def add_order(request):

    if request.method == 'POST':
        # An order was added
        order_form = OrderForm(data=request.POST)
        if order_form.is_valid():
            new_order = Order(**order_form.cleaned_data)
            new_order.save()
            return HttpResponseRedirect(reverse('mystore:detail', args=(new_order.id,)))
    else:
        order_form = OrderForm()
    return render(request, 'mystore/add_order.html', {'order_form': order_form})
