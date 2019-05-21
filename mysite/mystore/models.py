from django.db import models

from django.utils import timezone

from django.contrib.auth.models import User
from django.db.models import Sum

class Order(models.Model):
    order = models.SlugField(max_length=250, unique_for_date='created')
    created = models.DateTimeField(auto_now_add=True)
    client = models.CharField(max_length=25)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField('Item', through='qty')

    def add_items(self):
        return self.items.aggregate(total=models.Sum('price'))['total']

    def add_all_items(self):
        cnt = 0
        for qty in self.qty_set.all():
            cnt += qty.add_same_items()
        return cnt



class Item(models.Model):
    STATUS_CHOICES = (('outStock', 'OutStock'),
                      ('inStock', 'InStock'),)
    TYPE_CHOICES = (('pants', 'Pants'),
                      ('shirt', 'Shirt'),)


    item_name = models.CharField(max_length=25)
    slug = models.SlugField(max_length=250, unique_for_date='created')

    size = models.CharField(max_length=25)
    price = models.FloatField(default=0)
    item_type = models.CharField(max_length=10,
                                 choices=TYPE_CHOICES,
                                 default='pants')
    quantity = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='inStock',
                              )

    class Meta:
        ordering = ('-created',)
    def __str__(self):
        return self.item_name

class qty(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def add_same_items(self):
        return  self.quantity * self.item.price






