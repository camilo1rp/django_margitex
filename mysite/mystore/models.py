from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class Client(models.Model):
    name = models.CharField(max_length=60, verbose_name='Nombre')
    phone =  models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Telefono', unique=True)
    email = models.EmailField(blank=True)
    def __str__(self):
        return self.name + " - " + str(self.phone)[-3::]
    class Meta:
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'

class Order(models.Model):
    CONFIRM_CHOICES = ((False, 'Borrador'), (True, 'Confirmado'),)
    order = models.CharField(max_length=140, verbose_name='descripción / notas', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, null=True, on_delete=models.SET_NULL, verbose_name='cliente')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField('Item', through='Qty')
    comments = models.TextField(max_length=140, blank=True, verbose_name='comentarios')
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=9, decimal_places=2,
                               default=0, verbose_name='abono')
    #paid = models.DecimalField(max_digits=9, decimal_places=2,
     #                          default=0, verbose_name='abono', validators=[MinValueValidator(0.00)])

    discount = models.DecimalField(max_digits=9, decimal_places=2,
                               default=0, verbose_name='descuento')
    debt = models.DecimalField(max_digits=9, decimal_places=2, default=0, verbose_name='saldo')
    due_date = models.DateField(default= datetime.now()+timedelta(days=15),
                                verbose_name= 'Fecha de entrega', help_text="ejemplo: 2019-05-28")
    confirmed = models.BooleanField(choices=CONFIRM_CHOICES, default=False)
    completed = models.BooleanField(default=False)

    def add_items(self):
        return self.items.aggregate(total=models.Sum('price'))['total']

    def add_all_items(self):
        cnt = 0
        for qty in self.qty_set.all():
            cnt += qty.add_same_items()
            self.total = cnt
        return cnt

    def debts(self):
        self.debt = self.total - self.paid - self.discount

    def save(self, *args, **kwargs):
        if self.total == self.paid and self.paid != 0:
            self.completed = True
        super(Order, self).save(*args, **kwargs)





    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

class Institution(models.Model):
    name = models.CharField(max_length=50, verbose_name='nombre')
    name_slug = models.SlugField(unique=True, primary_key=True,
                                 max_length=50, verbose_name='codigo')
    def __str__(self):
        return self.name_slug

    class Meta:
        verbose_name = 'Institución/Categoria'
        verbose_name_plural = 'Instituciones/Categoria'

class Item(models.Model):
    name = models.CharField(max_length=90, verbose_name='nombre')
    size = models.CharField(max_length=25, verbose_name='talla')
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0,
                                verbose_name='precio')
    #type = models.CharField(max_length=20)
    quantity = models.IntegerField(default=0, verbose_name='cantidad')
    created = models.DateTimeField(auto_now_add=True, verbose_name='creado')
    updated = models.DateTimeField(auto_now=True, verbose_name='actualizado')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE,
                                    primary_key=False, verbose_name='institución')
    code = models.SlugField(max_length=90, verbose_name='codigo')
    prod_cost = models.DecimalField(max_digits=9, decimal_places=2, default=0,
                                verbose_name='precio producción')
    quantity_ordered = models.IntegerField(default=0, verbose_name='cantidad ordenada')
    quantity_needed = models.IntegerField(default=0, verbose_name='cantidad necesitada')

    def item_needed(self):
        sum = self.quantity_ordered - self.quantity
        if sum < 0:
            sum = 0
        self.quantity_needed = sum
        return sum

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        #if not self.code:
        self.code = slugify(self.name) + slugify(self.size) + slugify(self.institution)
        super(Item, self).save(*args, **kwargs)


    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'


class Qty(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    pending = models.IntegerField(default=1)

    def add_same_items(self):
        return self.quantity * self.item.price

    def get_dispatched_items(self):
        return  self.quantity - self.pending


class Payments(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    created = models.DateTimeField(auto_now_add=True)





