import weasyprint
from django.conf import settings
from django.contrib.postgres.search import SearchVector, SearchQuery, \
    SearchRank, TrigramSimilarity
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, \
    PageNotAnInteger
from django.db.models.functions import Greatest
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import ListView

from .forms import OrderForm, SelForm, EmailPostForm, \
    SearchForm, ClientSearchForm, ClientForm, ItemSearchForm
from .models import Order, Item, Institution, Client, Payments


def IndexView(request):
    form = SearchForm()
    query = None
    if 'pedido' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['pedido']
            search_vector = SearchVector('id', 'client')
            search_query =SearchQuery(query)
            results = Order.objects.annotate(search=search_vector, rank=SearchRank(search_vector, search_query))\
                .filter(search=search_query).order_by('-rank')
    else:
        #results = Order.objects.filter(debt__gt=F('total')).order_by('created')
        results = Order.objects.all().order_by('-created')
    #context_object_name = 'orders'
    object_list = results
    paginator = Paginator(object_list, 10)  # 3 orders in each page
    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer deliver the first page
        orders = paginator.page(1)
    except EmptyPage:
    # If page is out of range deliver last page of results
        orders = paginator.page(paginator.num_pages)

    return render(request, 'mystore/index.html', {'form': form,
                                                   'query': query,
                                                   'orders': orders
                                                   })

def detail(request, order_id, item_rmv=None, institution=None,
           size=None, item_dispatch=None, item_pending=None, item_missing=None):
    order = get_object_or_404(Order, pk=order_id)
    order.add_all_items()
    order_items_qty = order.qty_set.all().order_by('id')
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
                                                   'order_items_qty': order_items_qty,
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

    if order.confirmed == False:
        order_items = order.qty_set.all()
        for item in order_items:
            dispatched = item.quantity - item.pending
            if dispatched >= 0:
                item_stock = Item.objects.get(code=item.item)
                item_stock.quantity -= dispatched
                item_stock.quantity_ordered += item.pending
                item_stock.item_needed()
                item_stock.save()
        order.confirmed = True
        order.save()
        return HttpResponseRedirect(reverse('mystore:confirmation',
                                            args=(order.id,)))
    return render(request, 'mystore/confirmation.html', {'order': order})

def receipt(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    tax = float(order.total) * 0.19
    order.debts()
    order.save()
    return render(request, 'mystore/receipt.html', {'order': order,
                                                    'tax': tax})

def order_update(request, order_id, item_dispatch=None,
                 item_missing=None, item_pending=0,):
    order = get_object_or_404(Order, pk=order_id)
    order_items_qty = order.qty_set.all().order_by('id')
    if item_dispatch != None:
        item_dispatched = order.qty_set.get(id=item_dispatch)
        if item_pending !=0:
            item_dispatched.pending -= 1
            item_dispatched.save()
            product = Item.objects.get(code=item_dispatched.item)
            product.quantity -= 1
            product.quantity_ordered -= 1
            product.item_needed()
            product.save()
        return HttpResponseRedirect(reverse('mystore:order_update', args=(order.id,)))

    if item_missing != None:
        item_dispatched = order.qty_set.get(id=item_missing)
        if item_pending < item_dispatched.quantity:
            item_dispatched.pending += 1
            item_dispatched.save()
            product = Item.objects.get(code=item_dispatched.item)
            product.quantity += 1
            product.quantity_ordered += 1
            product.item_needed()
            product.save()
        return HttpResponseRedirect(reverse('mystore:order_update', args=(order.id,)))

    return render(request, 'mystore/order_update.html', {'order': order,
                                                         'order_items_qty': order_items_qty,
                                                         })

def order_share(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    sent= False
    products = []
    for product in order.qty_set.all():
        same_item_price = str(product.add_same_items())
        products += product.item.code + ": cantidad:" + str(product.quantity) +\
                    " Precio: $" + same_item_price + ".   "
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

class ItemSearchListView(ListView):
    template_name = "mystore/item_search.html"
    model = Item
    form_class = ItemSearchForm
    context_object_name = 'products'
    query = None
    def get_queryset(self):
        self.form = self.form_class(self.request.GET)
        if self.form.is_valid():
            self.query = self.form.cleaned_data['producto']
            if self.query:
                return Item.objects.annotate(similarity=Greatest(TrigramSimilarity('name', self.query),
                                                                  TrigramSimilarity('code', self.query))
                                              ).filter(similarity__gt=0.1).order_by('-similarity')


    def get_context_data(self, *args, **kwargs):
        context = super(ItemSearchListView, self).get_context_data(*args, **kwargs)
        context['form'] = self.form
        context['query'] = self.query
        return context

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

class InventoryListView(ListView):
    queryset = Item.objects.all().order_by('-quantity_needed', 'quantity')
    context_object_name = 'products'
    paginate_by = 10
    template_name ="mystore/inventory.html"

def client_detail(request, client):
    client_obj = get_object_or_404(Client, pk=client)
    #context_object_name = 'client'
    results = client_obj.order_set.all().order_by('id')
    object_list = results
    paginator = Paginator(object_list, 3)  # 3 client in each page
    page = request.GET.get('page')
    try:
        clients = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer deliver the first page
        clients = paginator.page(1)
    except EmptyPage:
    # If page is out of range deliver last page of results
        clients = paginator.page(paginator.num_pages)

    return render(request, 'mystore/client_detail.html', {'client': client_obj,
                                                          'client_page': clients,})

def add_client(request):
    if request.method == 'POST':
        # An order was added
        client_form = ClientForm(data=request.POST)
        if client_form.is_valid():
            new_client = Client(**client_form.cleaned_data)
            new_client.save()
            return HttpResponseRedirect(reverse('mystore:add_order',))
    else:
        client_form = ClientForm()
    return render(request, 'mystore/add_client.html', {'client_form': client_form})

def order_pdf(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    tax = float(order.total) * 0.19
    order.debts()
    order.save()
    html = render_to_string('mystore/order_receipt.html',{'order': order,
                                                    'tax': tax})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=\
    "order_{}.pdf"'.format(order.id)
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=[weasyprint.CSS(
        settings.STATIC_ROOT + 'mystore/style.css')])
    return response

def add_item(request,):
    if request.method == 'POST':
        try:

            institution = Institution.objects.get(pk=request.POST['inst'])
            code = request.POST['name'] + "-" + \
            request.POST['size'] + "-" + institution.name_slug
            product = Item.objects.get(code=code.lower())
            quantity_to_add = request.POST['quantity']
        except (KeyError, Item.DoesNotExist):
            return render(request, 'mystore/add_item.html',
                          {'error_message': "Error al agregar. Intentalo de nuevo!"})
        except (KeyError, Institution.DoesNotExist):
            return render(request, 'mystore/add_item.html',
                          {'error_message': "Error al agregar. Intentalo de nuevo!"})

        else:
            product.quantity += int(quantity_to_add)
            product.item_needed()
            product.save()
            return render(request, 'mystore/add_item.html',
                          {'error_message': "Se ha agreado al inventortio! usa el formulario para agregar mas productos"})


    return render(request, 'mystore/add_item.html')

def order_payments(request):
    order = get_object_or_404(Order, pk=request.POST['order_id'])
    amount_paid = request.POST['amount']
    amount_paid = int(amount_paid)
    #if order.debt > amount_paid:
    order.paid += amount_paid
    order.save()
    order.debts()
    order.save()
    pay = Payments(order=order, payment=amount_paid)
    pay.save()
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)

