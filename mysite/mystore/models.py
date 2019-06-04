from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone

class Order(models.Model):
    order = models.CharField(max_length=25)
    created = models.DateTimeField(auto_now_add=True)
    client = models.CharField(max_length=25)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField('Item', through='Qty')
    comments = models.TextField(max_length=140)
    def add_items(self):
        return self.items.aggregate(total=models.Sum('price'))['total']

    def add_all_items(self):
        cnt = 0
        for qty in self.qty_set.all():
            cnt += qty.add_same_items()
        return cnt

class Institution(models.Model):
    name = models.CharField(unique=True, primary_key=True, max_length=30)
    def __str__(self):
        return self.name



class Item(models.Model):
    name = models.CharField(max_length=25)
    size = models.CharField(max_length=25)
    price = models.FloatField(default=0)
    type = models.CharField(max_length=20)
    quantity = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, primary_key=False)
    code = models.CharField(max_length=25)
    class Meta:
        ordering = ('-created',)
    def __str__(self):
        return self.code


class Qty(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    pending = models.IntegerField(default=1)
    total = models.IntegerField(default=0)

    def add_same_items(self):
        return  self.quantity * self.item.price







