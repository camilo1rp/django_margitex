from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .forms import OrderForm, SelForm, ConfirmForm, EmailPostForm, \
    SearchForm, ClientSearchForm

from .models import Order, Item, Institution, Client
from django.core.mail import send_mail
from datetime import datetime, timedelta
from django.contrib.postgres.search import SearchVector, SearchQuery, \
    SearchRank, TrigramSimilarity
from django.db.models.functions import Greatest
from django.core.paginator import Paginator, EmptyPage,\
PageNotAnInteger

class IndexView(generic.ListView):
    #template_name = 'mystore/index.html'
    #context_object_name = 'latest_order_list'
    queryset = Order.objects.all()
    context_object_name = 'orders'
    paginate_by = 5
    template_name = 'mystore/index.html'

    #def get_queryset(self):
        #return Order.objects.all()


def detail(request, order_id, item_rmv=None, institution=None,
           size=None, item_dispatch=None, item_pending=None, item_missing=None):
    order = get_object_or_404(Order, pk=order_id)
    order.add_all_items()
    order_items_qty = order.qty_set.all()
    order.save()
    #check if any filter and assign the response
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

    if item_missing != None:
        item_dispatched = order.qty_set.get(id=item_missing)
        if item_pending < item_dispatched.quantity:
            item_dispatched.pending += 1
            item_dispatched.save()
        return response_page

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
                                                   'institution': institution, 'size': size},)


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

def confirmation(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        form = ConfirmForm(request.POST or None, instance=order)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('mystore:confirmation', args=(order.id,)))
    else:
        order_items = order.qty_set.all()
        for item in order_items:
            dispatched = item.quantity - item.pending
            if dispatched > 0:
                item_stock = Item.objects.get(code=item.item)
                item_stock.quantity -= dispatched
                item_stock.save()

        order.debt()
        order.save()
        form = ConfirmForm({'due_date':datetime.now()+timedelta(days=15)})
    return render(request, 'mystore/confirmation.html', {'form': form,
                                                     'order': order})

def receipt(request):
    return render(request, 'mystore/receipt.html')

def order_update(request, order_id, item_dispatch=None,
                 item_missing=None, item_pending=0,):

    order = get_object_or_404(Order, pk=order_id)

    if item_dispatch != None:
        item_dispatched = order.qty_set.get(id=item_dispatch)
        if item_pending !=0:
            item_dispatched.pending -= 1
            item_dispatched.save()
        return HttpResponseRedirect(reverse('mystore:order_update', args=(order.id,)))

    if item_missing != None:
        item_dispatched = order.qty_set.get(id=item_missing)
        if item_pending < item_dispatched.quantity:
            item_dispatched.pending += 1
            item_dispatched.save()
        return HttpResponseRedirect(reverse('mystore:order_update', args=(order.id,)))

    if request.method == 'POST':
        amount = request.POST['amount']
        amount_int = int(amount)
        order.debt()
        if order.debt >= amount_int:
            order.paid += amount_int
            order.save()
            return HttpResponseRedirect(reverse('mystore:order_update', args=(order.id,)))
        else:
            return render(request, 'mystore/order_update.html',
                        {'order': order,
                        'error_message': "Abono supera el costo total"})
    else:
        order_items=order.qty_set.all()
        for item in order_items:
            dispatched = item.quantity - item.pending
            if dispatched > 0:
                item_stock = Item.objects.get(code=item.item)
                item_stock.quantity -= dispatched
                item_stock.save()

    order.debt()
    order.save()
    return render(request, 'mystore/order_update.html', {'order': order})

def order_share(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    sent= False
    products = "Poductos: "
    for product in order.qty_set.all():
        same_item_price = str(product.add_same_items())
        products += product.item.code + ": cantidad:" + str(product.quantity) +\
                    " Precio: $" + same_item_price + " /// "
    #products = products[0:-2]
    if request.method == 'POST':
    # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
        # Form fields passed validation
            cd = form.cleaned_data
            subject = 'Gracias por tu compra, Margitex. Pedido: N0{}'.format(order.id)
            message = '{} tu pedido ha sido recibido\n\nProductos: {}. \n total:{} \n'\
                .format(cd['name'], products, order.total)
            send_mail(subject, message, 'margitex@margitex.com',[cd['to']])
            sent= True
        # ... send email
    else:
        form = EmailPostForm({'name':order.client.name,
                              'email':'margitex@gmail.com',
                              'to': order.client.email,
                              'content':products
                              })

    return render(request, 'mystore/share.html', {'order': order,
                                                  'form': form,
                                                  'sent': sent,
                                                  })
def order_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'pedido' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['pedido']
            search_vector = SearchVector('id', 'client')
            search_query =SearchQuery(query)
            results = Order.objects.annotate(search=search_vector, rank=SearchRank(search_vector, search_query))\
                .filter(search=search_query).order_by('-rank')
    return render(request, 'mystore/search.html',{'form': form,
                                                    'query': query,
                                                    'results': results
                                                    })
def client_search(request):
    form = ClientSearchForm()
    query = None
    results = []
    if 'buscador' in request.GET:
        form = ClientSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['buscador']
            #search_vector = SearchVector('name', 'phone', 'email')
            #search_query =SearchQuery(query)
            results = Client.objects.annotate(similarity=Greatest(TrigramSimilarity('name', query),
                                                                  TrigramSimilarity('email', query))
                                              ).filter(similarity__gt=0.1).order_by('-similarity')
    return render(request, 'mystore/client_search.html',{'form': form,
                                                        'query': query,
                                                        'results': results
                                                        })

