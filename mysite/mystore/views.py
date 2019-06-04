from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .forms import OrderForm, SelForm

from .models import Order, Item, Institution


class IndexView(generic.ListView):
    template_name = 'mystore/index.html'
    context_object_name = 'latest_order_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Order.objects.all()

def detail(request, order_id, item_rmv=None, institution=None, size=None, item_dispatch=None, item_pending=None):
    order = get_object_or_404(Order, pk=order_id)

    #check if any filter and assign the response
    if institution == None:
        response_page = HttpResponseRedirect(reverse('mystore:detail', args=(order.id,)))
    else:
        if size == None:
            response_page = HttpResponseRedirect(reverse('mystore:institution',
                                                         args=(order.id,
                                                               institution)))
        else:
            response_page = HttpResponseRedirect(reverse('mystore:size', args=(order.id,
                                                                      institution,
                                                                      size)))
    #check if an item is to be removed
    if item_rmv != None:
        item_to_remove = order.qty_set.get(id=item_rmv)
        if item_to_remove.quantity == 1:
            order.qty_set.filter(id=item_rmv).delete()
            order.save()
            return response_page
        else:
            item_to_remove.quantity = item_to_remove.quantity - 1
            if item_to_remove.pending == 0:
                item_to_remove.save()
            else:
                item_to_remove.pending -= 1
                item_to_remove.save()
            return response_page

    if item_dispatch != None:
        item_dispatched = order.qty_set.get(id=item_dispatch)
        if item_pending !=0:
            item_dispatched.pending -= 1
            item_dispatched.save()
        return response_page

    order_items_qty = order.qty_set.all()
    if request.method == 'POST':
        form = SelForm(request.POST)
        if form.is_valid():
            new_item = form.save(commit=False)
            item_form = new_item.item
            for qty in order_items_qty:
                if item_form == qty.item:
                    qty.quantity += 1
                    qty.pending +=1
                    qty.save()
                    order.save()
                    return response_page
            new_item.order = order
            new_item.save()
            return response_page
        else:
            try:
                institution = Institution.objects.get(pk=request.POST['inst'])
                size = request.POST['size']
            except (KeyError, Institution.DoesNotExist):
                # Redisplay the question voting form.
                form = SelForm()
                form.fields["item"].queryset = Item.objects.all()
            else:
                if size == None:
                    form.fields["item"].queryset = Item.objects.\
                        filter(institution=institution)
                    return HttpResponseRedirect(reverse('mystore:institution', args=(order.id,
                                                         institution)))
                else:
                    form = SelForm()
                    form.fields["item"].queryset = Item.objects. \
                        filter(institution=institution, size=size)
                    return HttpResponseRedirect(reverse('mystore:size', args=(order.id,
                                                                              institution,
                                                                              size)))
    else:
        if institution == None:
            form = SelForm()
        else:
            if size == None:
                form = SelForm()
                form.fields["item"].queryset = Item.objects. \
                                    filter(institution=institution)
            else:
                form = SelForm()
                form.fields["item"].queryset = Item.objects. \
                    filter(institution=institution, size=size)
    return render(request, 'mystore/detail.html', {'form': form,
                                                   'order': order,
                                                   'institution': institution},)


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


